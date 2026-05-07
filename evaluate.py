import time
import json
import logging
from typing import Dict, List
from model import GameRecommender
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class RecommenderEvaluator:
    def __init__(self):
        self.recommender = GameRecommender(Config)
        if not self.recommender.initialize(force_rebuild=False):
            raise RuntimeError("Model_Init_Fail")

    def measure_latency(self, queries: List[str], iterations: int = 10) -> Dict[str, float]:
        latencies = []
        for q in queries:
            start_time = time.perf_counter()
            for _ in range(iterations):
                self.recommender.recommend_games(q, n=15)
            end_time = time.perf_counter()
            avg_latency = ((end_time - start_time) / iterations) * 1000
            latencies.append(avg_latency)
        
        return {
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "max_latency_ms": round(max(latencies), 2),
            "min_latency_ms": round(min(latencies), 2)
        }

    def evaluate_recall_at_k(self, test_cases: Dict[str, List[str]], k: int = 15) -> float:
        hits = 0
        total = len(test_cases)
        
        for source_game, expected_games in test_cases.items():
            results = self.recommender.recommend_games(source_game, n=k)
            result_names = [r["Name"].lower() for r in results]
            
            for expected in expected_games:
                if any(expected.lower() in res_name for res_name in result_names):
                    hits += 1
                    break
                    
        return round((hits / total) * 100, 2) if total > 0 else 0.0

    def test_weight_variance(self, query: str) -> Dict[str, List[str]]:
        weight_configs = {
            "default": {},
            "pure_visual": {"visual": 1.0, "vector": 0.0, "tag": 0.0, "genre": 0.0, "quality": 0.0, "playtime": 0.0, "era": 0.0},
            "pure_mechanic": {"tag": 1.0, "vector": 0.0, "genre": 0.0, "visual": 0.0, "quality": 0.0, "playtime": 0.0, "era": 0.0},
            "pure_era": {"era": 1.0, "vector": 0.0, "tag": 0.0, "genre": 0.0, "visual": 0.0, "quality": 0.0, "playtime": 0.0}
        }
        
        variance_results = {}
        for config_name, weights in weight_configs.items():
            filters = {"weights": weights} if weights else None
            results = self.recommender.recommend_games(query, n=5, filters=filters)
            variance_results[config_name] = [r["Name"] for r in results]
            
        return variance_results

    def run_suite(self):
        logger.info("Evaluation Suite Started")
        
        latency_queries = ["Half-Life", "The Witcher 3", "Stardew Valley", "Grand Theft Auto V", "Portal 2"]
        latency_metrics = self.measure_latency(latency_queries)
        
        recall_cases = {
            "Dark Souls": ["Elden Ring", "Bloodborne", "Sekiro"],
            "Stardew Valley": ["Harvest Moon", "Animal Crossing", "Graveyard Keeper", "Terraria"],
            "Left 4 Dead 2": ["Warhammer: Vermintide 2", "Back 4 Blood", "Payday 2", "Deep Rock Galactic"],
            "Cities: Skylines": ["SimCity", "Planet Coaster", "Factorio"],
            "Hollow Knight": ["Ori and the Blind Forest", "Dead Cells", "Blasphemous", "Celeste"]
        }
        recall_score = self.evaluate_recall_at_k(recall_cases, k=15)
        
        variance_test = self.test_weight_variance("Cyberpunk 2077")
        
        report = {
            "Performance_Metrics": latency_metrics,
            "Quality_Recall_At_15_Percent": recall_score,
            "Weight_Variance_Test_Cyberpunk_2077": variance_test
        }
        
        print("\n" + "="*50)
        print("EVALUATION REPORT")
        print("="*50)
        print(json.dumps(report, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    evaluator = RecommenderEvaluator()
    evaluator.run_suite()