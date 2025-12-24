import csv
import math
import re
from pathlib import Path
from typing import List, Dict

# 定义全局知识库缓存
OCEAN_KNOWLEDGE_BASE = []


def get_embedding(text: str) -> Dict[str, int]:
    """
    简单的词袋模型向量化：把句子变成单词计数的字典
    """
    words = re.findall(r'\w+', text.lower())
    vec = {}
    for w in words:
        vec[w] = vec.get(w, 0) + 1
    return vec


def cosine_similarity(vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
    """
    计算两个向量的余弦相似度（匹配度）
    """
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    return numerator / denominator if denominator else 0.0


def load_knowledge(csv_path_str: str):
    """
    读取 CSV 数据，一定要适配最新的 create_data.py 生成的格式
    """
    global OCEAN_KNOWLEDGE_BASE

    # 1. 自动寻找 data 文件夹里的 ocean_rich_data.csv
    current_file = Path(__file__).resolve()
    # 往上跳4级找到项目根目录
    project_root = current_file.parent.parent.parent.parent
    path = project_root / "data" / "ocean_data.csv"

    print(f"[知识库] 正在加载数据文件：{path.name}")

    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                OCEAN_KNOWLEDGE_BASE = []  # 清空旧缓存

                count = 0
                for row in reader:
                    # === 核心修改：适配新数据格式 ===
                    # 把 深度(depth_m) 和 类型(depth_type) 都读进去,这样每一层的描述都独一无二

                    # 容错处理：万一 uuid 列没生成，就用行号
                    uid = row.get("unique_id", f"row-{count}")

                    content = (
                        f"[来源ID：{uid}]"  
                        f"【{row.get('region', '未知区域')}】 "
                        f"深度:{row.get('depth_m', '0')}米 ({row.get('depth_type', '未知层')})\n"
                        f"   - 物理环境: 温度 {row.get('temperature')}°C, 盐度 {row.get('salinity')}‰\n"
                        f"   - 生物群落: {row.get('marine_life')}\n"
                        f"   - 详细描述: {row.get('description')}"
                    )

                    OCEAN_KNOWLEDGE_BASE.append({
                        "id": uid,  # 记录ID，防止重复
                        "content": content,
                        "vector": get_embedding(content)  # 建立索引
                    })
                    count += 1

            print(f"✅ 成功加载了 {len(OCEAN_KNOWLEDGE_BASE)} 条数据")

        except Exception as e:
            print(f"❌ 读取 CSV 出错: {e}")
    else:
        print(f"❌ 找不到文件：{path}")


def semantic_search(query: str, top_k: int = 20) -> str:

    print(f"[知识库] 正在全层扫描关键词: '{query}'")

    if not OCEAN_KNOWLEDGE_BASE:
        return "知识库为空，请检查初始化。"

    query_vec = get_embedding(query)
    scored_results = []

    for item in OCEAN_KNOWLEDGE_BASE:
        score = cosine_similarity(query_vec, item["vector"])
        # 只要有一点相关性（大于0）就列入候选
        if score > 0:
            scored_results.append((score, item))

    # 按分数排序
    scored_results.sort(key=lambda x: x[0], reverse=True)

    # 取前 top_k 个
    # 因为同一个地点可能有 4-5 个不同深度的数据，所以 top_k 必须够大
    results = [item["content"] for score, item in scored_results[:top_k]]

    if not results:
        return "知识库中未找到匹配数据。"

    # 用醒目的分割线拼接
    return "\n" + "-" * 30 + "\n".join(results) + "\n" + "-" * 30