import itertools
import json
import os
from datetime import datetime
from collections import defaultdict

try:
    import pulp
except ImportError:
    pulp = None
    print("警告：未安装 pulp 库，ILP 算法不可用。请使用 pip install pulp 安装。")

def combinations(iterable, r):
    """Helper function for combinations."""
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, r):
            indices[j] = indices[j - 1] + 1
        yield tuple(pool[i] for i in indices)

def greedy_optimal_selection(n_samples, k, j, s, coverage=1):
    """使用贪心算法选择最优的 k 样本组。

    目标：找到最小数量的 k 样本组，使得对于 *每一个* 从 n 个样本中选出的 j 样本组，
    都至少有一个选定的 k 样本组包含了该 j 样本组的至少 coverage 个 s 子组。

    Args:
        n_samples (list): 随机选择的 n 个样本列表。
        k (int): 要选择的样本组的大小。
        j (int): 从 n 个样本中选择的子集大小。
        s (int): 从 j 个样本子集中需要覆盖的样本数量。
        coverage (int): 每个 k 样本组需要覆盖的 j 样本子集的最小数量，默认为1（至少ONE）。

    Returns:
        list: 选定的 k 样本组列表。
    """
    n = len(n_samples)
    if not (s <= j <= k <= n):
        raise ValueError("参数必须满足 s <= j <= k <= n")

    #生成所有可能的 k 样本组
    possible_k_groups = list(combinations(n_samples, k))
    k_groups_sets = [set(group) for group in possible_k_groups]
    num_k_groups = len(possible_k_groups)

    #生成所有 j 样本组
    j_groups_tuples = list(combinations(n_samples, j))
    j_groups = [frozenset(group) for group in j_groups_tuples]

    #为每个 j 样本组生成其所有 s 子组
    j_group_to_s_subgroups = defaultdict(set)
    for j_group_tuple in j_groups_tuples:
        j_group_fset = frozenset(j_group_tuple)
        for s_subgroup_tuple in combinations(j_group_tuple, s):
            j_group_to_s_subgroups[j_group_fset].add(frozenset(s_subgroup_tuple))

    # 选择
    selected_k_group_indices = set()
    # 跟踪每个j组被覆盖的次数
    j_group_coverage_count = {j_fset: 0 for j_fset in j_groups}
    # 初始时所有j组都未满足覆盖度要求
    unsatisfied_j_groups = set(j_groups)

    # 预计算每个 k 组能满足哪些 j 组
    k_group_satisfies_j_groups = defaultdict(set)
    for idx, k_set in enumerate(k_groups_sets):
        for j_fset, s_sub_fsets in j_group_to_s_subgroups.items():
            for s_fset in s_sub_fsets:
                if s_fset.issubset(k_set):
                    k_group_satisfies_j_groups[idx].add(j_fset)
                    break

    while unsatisfied_j_groups:
        best_k_group_index = -1
        max_newly_satisfied_count = -1
        newly_satisfied_by_best = set()

        # 寻找能满足最多 *未满足* j 组的 k 组
        # 迭代所有 *尚未选择* 的 k 组索引
        candidate_indices = set(range(num_k_groups)) - selected_k_group_indices
        if not candidate_indices:
             print("警告：没有更多候选 k 组，但仍有未满足的 j 组。可能无解或贪心策略失败。")
             break

        for k_idx in candidate_indices:
            currently_satisfies = k_group_satisfies_j_groups[k_idx]
            newly_satisfied = currently_satisfies.intersection(unsatisfied_j_groups)
            count = len(newly_satisfied)

            if count > max_newly_satisfied_count:
                max_newly_satisfied_count = count
                best_k_group_index = k_idx
                newly_satisfied_by_best = newly_satisfied

        if best_k_group_index == -1 or max_newly_satisfied_count == 0:
            print("警告：无法找到能满足更多未满足 j 组的 k 组。流程终止。")
            break

        selected_k_group_indices.add(best_k_group_index)
        
        # 更新每个j组的覆盖计数
        for j_group in newly_satisfied_by_best:
            j_group_coverage_count[j_group] += 1
            # 如果达到了覆盖度要求，从未满足集合中移除
            if j_group_coverage_count[j_group] >= coverage:
                unsatisfied_j_groups.remove(j_group)

    final_selected_k_groups = [possible_k_groups[i] for i in selected_k_group_indices]

    return final_selected_k_groups

def save_results(m, n, k, j, s, selected_groups, run_index, coverage=1):
    """将结果保存到 JSON 文件。"""
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 文件名格式调整为 project.txt 中的示例: m-n-k-j-s-coverage-run_index-num_results-timestamp.json
    filename = f"{m}-{n}-{k}-{j}-{s}-{coverage}-{run_index}-{len(selected_groups)}-{timestamp}.json"
    filepath = os.path.join(results_dir, filename)

    data_to_save = {
        'parameters': {'m': m, 'n': n, 'k': k, 'j': j, 's': s, 'coverage': coverage},
        'run_index': run_index,
        'selected_k_groups': [list(group) for group in selected_groups]
    }

    with open(filepath, 'w') as f:
        json.dump(data_to_save, f, indent=4)
    print(f"结果已保存到: {filepath}")
    return filepath

 # 或者可以返回空列表或其他指示失败的值

# --- 主程序逻辑 (示例) ---
if __name__ == "__main__":
    # 示例参数 (对应 E.g. 3 from project.txt)
    m_val = 45
    n_val = 9
    k_val = 6
    j_val = 4
    s_val = 4
    # 假设随机选择了 n 个样本
    n_samples_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'] # 对应 E.g. 3
    run_id = 1 # 假设是第一次运行

    print(f"输入参数: m={m_val}, n={n_val}, k={k_val}, j={j_val}, s={s_val}")
    print(f"选定的 n 个样本: {n_samples_list}")

    try:
        optimal_groups = greedy_optimal_selection(n_samples_list, k_val, j_val, s_val)
        print("\n选定的最优 k 样本组 (贪心算法):")
        # 对结果进行排序以便比较
        sorted_optimal_groups = sorted([tuple(sorted(group)) for group in optimal_groups])
        for i, group in enumerate(sorted_optimal_groups):
            print(f"  {i+1}. {','.join(group)}")

        print(f"\n总共找到 {len(optimal_groups)} 组。")

        # 注意：贪心算法不保证找到全局最优解（最小数量的组）。
        # E.g. 3 的预期结果是 12 组，贪心算法可能得到不同数量的结果。

        # 保存结果 (取消注释以启用)
        # save_results(m_val, n_val, k_val, j_val, s_val, optimal_groups, run_id)

    except ValueError as e:
        print(f"错误: {e}")

    # 可以在此添加 GUI 逻辑或与其他模块集成


def ilp_optimal_selection(n_samples, k, j, s, coverage=1):
    """使用整数线性规划（ILP）选择最优的 k 样本组。
    目标与 greedy_optimal_selection 相同。
    需要安装 pulp 库。
    """
    if pulp is None:
        raise ImportError("未安装 pulp 库，无法使用 ILP 算法。请先安装 pulp。")
    n = len(n_samples)
    if not (s <= j <= k <= n):
        raise ValueError("参数必须满足 s <= j <= k <= n")
    
    # 检查是否在打包环境中运行
    import sys
    is_frozen = getattr(sys, 'frozen', False)
    # 1. 生成所有可能的 k 样本组 (nCk)
    possible_k_groups = list(combinations(n_samples, k))
    k_groups_sets = [set(group) for group in possible_k_groups]
    num_k_groups = len(possible_k_groups)
    # 2. 生成所有 j 样本组 (nCj)
    j_groups_tuples = list(combinations(n_samples, j))
    j_groups = [frozenset(group) for group in j_groups_tuples]
    # 3. 为每个 j 样本组生成其所有 s 子组 (jCs)
    j_group_to_s_subgroups = defaultdict(set)
    for j_group_tuple in j_groups_tuples:
        j_group_fset = frozenset(j_group_tuple)
        for s_subgroup_tuple in combinations(j_group_tuple, s):
            j_group_to_s_subgroups[j_group_fset].add(frozenset(s_subgroup_tuple))
    #建立 ILP 模型
    prob = pulp.LpProblem("OptimalSampleSelection", pulp.LpMinimize)
    # 决策变量
    x_vars = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(num_k_groups)]
    # 目标函数
    prob += pulp.lpSum(x_vars)
    # 约束
    for j_idx, j_fset in enumerate(j_groups):
        covering_k_indices = set()
        s_sub_fsets = j_group_to_s_subgroups[j_fset]
        for k_idx, k_set in enumerate(k_groups_sets):
            for s_fset in s_sub_fsets:
                if s_fset.issubset(k_set):
                    covering_k_indices.add(k_idx)
                    break
        if not covering_k_indices:
            raise ValueError(f"无法找到覆盖 j 组 {sorted(j_fset)} 的 k 组，参数设置可能有误。")
        # 修改约束，要求至少有coverage个k组覆盖每个j组
        prob += pulp.lpSum([x_vars[i] for i in covering_k_indices]) >= coverage, f"cover_j_{j_idx}"
    # 求解
    try:
        # 在打包环境中处理CBC求解器路径
        if is_frozen:
            import os
            # 获取应用程序的基础路径
            base_path = os.path.dirname(sys.executable) if is_frozen else os.path.dirname(os.path.abspath(__file__))
            # 尝试使用相对路径找到CBC求解器
            solver_path = os.path.join(base_path, "pulp", "solverdir", "cbc", "win", "i64", "cbc.exe")
            
            if os.path.exists(solver_path):
                solver = pulp.PULP_CBC_CMD(path=solver_path, msg=0)
            else:
                # 如果找不到求解器，尝试使用默认路径
                solver = pulp.PULP_CBC_CMD(msg=0)
        else:
            # 非打包环境使用默认路径
            solver = pulp.PULP_CBC_CMD(msg=0)
            
        result_status = prob.solve(solver)
        if result_status != pulp.LpStatusOptimal:
            raise RuntimeError("ILP 求解失败，未找到最优解。")
    except Exception as e:
        raise RuntimeError(f"ILP 求解过程出错: {str(e)}")
    selected_k_group_indices = [i for i, var in enumerate(x_vars) if var.value() == 1]
    final_selected_k_groups = [possible_k_groups[i] for i in selected_k_group_indices]
    return final_selected_k_groups


