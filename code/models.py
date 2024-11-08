import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix, csr_matrix, save_npz, load_npz
from typing import List, Dict
import os
from datetime import datetime, timedelta


class RecallModel:
    def __init__(self, long_term_decay: float, short_term_decay: float, storage_dir: str):
        self.storage_dir = storage_dir
        self.user_to_index = {}
        self.episode_to_index = {}
        self.index_to_user = []
        self.index_to_episode = []
        self.long_term_matrix = lil_matrix((0, 0), dtype=np.float32)
        self.short_term_matrix = lil_matrix((0, 0), dtype=np.float32)
        self.long_term_decay = long_term_decay
        self.short_term_decay = short_term_decay
        self.load_indices()

    def update_matrix(self, interactions: pd.DataFrame):
        self.long_term_matrix *= self.long_term_decay
        self.short_term_matrix *= self.short_term_decay

        interactions['interest_action'] = interactions['interest_action'].apply(lambda x: 1 if x != 0 else 0)
        for _, row in interactions.iterrows():
            user_id, episode_key, interest_action = row['user_id'], row['episode_key'], row['interest_action']
            user_index = self._get_or_add_user_index(user_id)
            episode_index = self._get_or_add_episode_index(episode_key)
            self.long_term_matrix[user_index, episode_index] += interest_action
            self.short_term_matrix[user_index, episode_index] += interest_action

        self._normalize_matrices()
        self.save_indices()

    def _get_or_add_user_index(self, user_id: str) -> int:
        if user_id not in self.user_to_index:
            user_index = len(self.index_to_user)
            self.user_to_index[user_id] = user_index
            self.index_to_user.append(user_id)
            self.long_term_matrix.resize((len(self.index_to_user), self.long_term_matrix.shape[1]))
            self.short_term_matrix.resize((len(self.index_to_user), self.short_term_matrix.shape[1]))
        return self.user_to_index[user_id]

    def _get_or_add_episode_index(self, episode_key: str) -> int:
        if episode_key not in self.episode_to_index:
            episode_index = len(self.index_to_episode)
            self.episode_to_index[episode_key] = episode_index
            self.index_to_episode.append(episode_key)
            self.long_term_matrix.resize((self.long_term_matrix.shape[0], len(self.index_to_episode)))
            self.short_term_matrix.resize((self.short_term_matrix.shape[0], len(self.index_to_episode)))
        return self.episode_to_index[episode_key]

    def _normalize_matrices(self):
        if self.long_term_matrix.nnz != 0:
            self.long_term_matrix /= self.long_term_matrix.max()
        if self.short_term_matrix.nnz != 0:
            self.short_term_matrix /= self.short_term_matrix.max()

    def recall(self, user_id: str, top_k: int) -> Dict[str, List[str]]:
        if user_id not in self.user_to_index:
            return {"long_term_recall": [], "short_term_recall": []}

        user_index = self.user_to_index[user_id]
        long_term_scores = self.long_term_matrix[user_index].toarray().flatten()
        short_term_scores = self.short_term_matrix[user_index].toarray().flatten()

        long_term_top_k_indices = np.argsort(-long_term_scores)[:top_k].tolist()
        short_term_top_k_indices = np.argsort(-short_term_scores)[:top_k].tolist()

        long_term_top_k = [self.index_to_episode[i] for i in long_term_top_k_indices]
        short_term_top_k = [self.index_to_episode[i] for i in short_term_top_k_indices]

        long_term_top_k = self.filter_known_positives(user_id, long_term_top_k)
        short_term_top_k = self.filter_known_positives(user_id, short_term_top_k)

        long_term_top_k_set = set(long_term_top_k)
        short_term_top_k = [item for item in short_term_top_k if item not in long_term_top_k_set]

        return {
            'long_term_recall': long_term_top_k,
            'short_term_recall': short_term_top_k
        }

    def filter_known_positives(self, user_id: str, candidates: List[str]) -> List[str]:
        user_index = self.user_to_index[user_id]
        known_positives = set(np.where(self.long_term_matrix[user_index].toarray().flatten() > 0)[0])
        known_positives = {self.index_to_episode[i] for i in known_positives}
        return [item for item in candidates if item not in known_positives]

    def save_indices(self):
        indices = {
            'user_to_index': self.user_to_index,
            'episode_to_index': self.episode_to_index,
            'index_to_user': self.index_to_user,
            'index_to_episode': self.index_to_episode
        }
        pd.to_pickle(indices, os.path.join(self.storage_dir, 'indices.pkl'))

    def load_indices(self):
        indices_path = os.path.join(self.storage_dir, 'indices.pkl')
        if os.path.exists(indices_path):
            indices = pd.read_pickle(indices_path)
            self.user_to_index = indices['user_to_index']
            self.episode_to_index = indices['episode_to_index']
            self.index_to_user = indices['index_to_user']
            self.index_to_episode = indices['index_to_episode']

    def save_matrices(self):
        long_term_path = os.path.join(self.storage_dir, 'long_term_matrix.npz')
        short_term_path = os.path.join(self.storage_dir, 'short_term_matrix.npz')
        save_npz(long_term_path, csr_matrix(self.long_term_matrix))
        save_npz(short_term_path, csr_matrix(self.short_term_matrix))

    def load_matrices(self):
        long_term_path = os.path.join(self.storage_dir, 'long_term_matrix.npz')
        short_term_path = os.path.join(self.storage_dir, 'short_term_matrix.npz')
        if os.path.exists(long_term_path):
            self.long_term_matrix = load_npz(long_term_path).tolil()
        if os.path.exists(short_term_path):
            self.short_term_matrix = load_npz(short_term_path).tolil()

    def reinitialize_model(self, start_date: str, end_date: str = None):
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')

        start_datetime = datetime.strptime(start_date, '%Y%m%d')
        end_datetime = datetime.strptime(end_date, '%Y%m%d')
        while start_datetime <= end_datetime:
            date_str = start_datetime.strftime('%Y%m%d')
            interactions = read_data(date=date_str)
            if interactions is not None and len(interactions) != 0:
                self.update_matrix(interactions)
                start_datetime += timedelta(days=1)
            else:
                continue


def read_data(date='20241105', directory='/Users/lilili/Desktop/projects/recsys/methods/cf/data', limit=10000):
    try:
        filename = f"{date}_dim_drama_eposides_labels_di.csv"
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            print(f"Loading drama data from {filepath}")
            return pd.read_csv(filepath)
        else:
            print(f"Reading drama data for date: {date}")
            row_num_limit = f"WHERE row_num <= {limit}" if limit else ""
            sql = f"""
                    SELECT * 
                    FROM (
                        SELECT episode_key, user_id, interest_action,
                               ROW_NUMBER() OVER () AS row_num
                        FROM drama_rec_dev.dim_drama_eposides_labels_di 
                        WHERE dt = '{date}'
                    ) subquery
                    {row_num_limit};
                """
            df = read_data(sql)
            return df
    except Exception as e:
        print(str(e))
        return None


def update_matrices(model: RecallModel):
    interactions = read_data()
    model.update_matrix(interactions)
    model.save_matrices()
    model.save_indices()


def recall_interface(model: RecallModel, user_id: str, top_k: int) -> Dict[str, List[str]]:
    return model.recall(user_id, top_k)
