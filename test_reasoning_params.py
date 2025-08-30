import json

def preprocess_last_user_message(messages, reasoning_effort=None, max_reasoning_tokens=None):
    """预处理最后一条用户消息，添加 reasoning 参数标记"""
    if not messages:
        return messages
    
    # 创建消息副本以避免修改原始列表
    processed_messages = [msg.copy() for msg in messages]
    
    # 获取最后一条消息
    last_message = processed_messages[-1]
    
    # 检查是否为用户消息且内容为字符串
    if last_message.get("role") == "user" and isinstance(last_message.get("content"), str):
        content = last_message["content"]
        
        # 检查是否已包含标记
        has_reasoning_effort = "--reasoning_effort=" in content
        has_thinking_budget = "--thinking_budget=" in content
        
        # 构建要追加的标记
        append_parts = []
        
        # 处理 reasoning_effort
        if reasoning_effort and reasoning_effort in ["minimal", "low", "medium", "high"] and not has_reasoning_effort:
            append_parts.append(f" --reasoning_effort={reasoning_effort}")
        
        # 处理 max_reasoning_tokens
        if max_reasoning_tokens is not None and not has_thinking_budget:
            try:
                budget = int(max_reasoning_tokens)
                # 裁剪范围到 0-30768
                budget = max(0, min(budget, 30768))
                append_parts.append(f" --thinking_budget={budget}")
            except (ValueError, TypeError):
                pass  # 忽略无效值
        
        # 如果有要追加的内容，则追加到消息末尾
        if append_parts:
            # 去除尾部空格后再追加
            content = content.rstrip()
            content += "".join(append_parts)
            last_message["content"] = content
    
    return processed_messages

def test_preprocess_last_user_message():
    """测试 preprocess_last_user_message 函数的各种情况"""
    
    # 测试用例1: 仅 reasoning_effort 参数
    print("测试用例1: 仅 reasoning_effort 参数")
    messages1 = [{"role": "user", "content": "Hello, how are you?"}]
    result1 = preprocess_last_user_message(messages1, reasoning_effort="high")
    expected1 = [{"role": "user", "content": "Hello, how are you? --reasoning_effort=high"}]
    assert result1 == expected1, f"期望 {expected1}, 实际 {result1}"
    print("通过\n")

    # 测试用例2: 仅 max_reasoning_tokens 参数
    print("测试用例2: 仅 max_reasoning_tokens 参数")
    messages2 = [{"role": "user", "content": "Calculate 123*456"}]
    result2 = preprocess_last_user_message(messages2, max_reasoning_tokens=1024)
    expected2 = [{"role": "user", "content": "Calculate 123*456 --thinking_budget=1024"}]
    assert result2 == expected2, f"期望 {expected2}, 实际 {result2}"
    print("通过\n")

    # 测试用例3: 两个参数都存在
    print("测试用例3: 两个参数都存在")
    messages3 = [{"role": "user", "content": "Explain quantum computing"}]
    result3 = preprocess_last_user_message(messages3, reasoning_effort="medium", max_reasoning_tokens=2048)
    expected3 = [{"role": "user", "content": "Explain quantum computing --reasoning_effort=medium --thinking_budget=2048"}]
    assert result3 == expected3, f"期望 {expected3}, 实际 {result3}"
    print("通过\n")

    # 测试用例4: 参数都不存在
    print("测试用例4: 参数都不存在")
    messages4 = [{"role": "user", "content": "What's the weather like?"}]
    result4 = preprocess_last_user_message(messages4)
    expected4 = [{"role": "user", "content": "What's the weather like?"}]
    assert result4 == expected4, f"期望 {expected4}, 实际 {result4}"
    print("通过\n")

    # 测试用例5: 最后一条消息不是 user
    print("测试用例5: 最后一条消息不是 user")
    messages5 = [{"role": "user", "content": "First message"}, {"role": "assistant", "content": "Response"}]
    result5 = preprocess_last_user_message(messages5, reasoning_effort="low")
    expected5 = [{"role": "user", "content": "First message"}, {"role": "assistant", "content": "Response"}]
    assert result5 == expected5, f"期望 {expected5}, 实际 {result5}"
    print("通过\n")

    # 测试用例6: 消息已包含标记
    print("测试用例6: 消息已包含标记")
    messages6 = [{"role": "user", "content": "Already has marker --reasoning_effort=high"}]
    result6 = preprocess_last_user_message(messages6, reasoning_effort="low")
    expected6 = [{"role": "user", "content": "Already has marker --reasoning_effort=high"}]
    assert result6 == expected6, f"期望 {expected6}, 实际 {result6}"
    print("通过\n")

    # 测试用例7: max_reasoning_tokens 边界值
    print("测试用例7: max_reasoning_tokens 边界值")
    messages7 = [{"role": "user", "content": "Test boundary values"}]
    result7a = preprocess_last_user_message(messages7, max_reasoning_tokens=-100)
    expected7a = [{"role": "user", "content": "Test boundary values --thinking_budget=0"}]
    assert result7a == expected7a, f"期望 {expected7a}, 实际 {result7a}"
    
    result7b = preprocess_last_user_message(messages7, max_reasoning_tokens=50000)
    expected7b = [{"role": "user", "content": "Test boundary values --thinking_budget=30768"}]
    assert result7b == expected7b, f"期望 {expected7b}, 实际 {result7b}"
    print("通过\n")

    # 测试用例8: 消息内容包含尾部空格
    print("测试用例8: 消息内容包含尾部空格")
    messages8 = [{"role": "user", "content": "Message with trailing spaces   "}]
    result8 = preprocess_last_user_message(messages8, reasoning_effort="minimal")
    expected8 = [{"role": "user", "content": "Message with trailing spaces --reasoning_effort=minimal"}]
    assert result8 == expected8, f"期望 {expected8}, 实际 {result8}"
    print("通过\n")

    print("所有测试用例通过!")

if __name__ == "__main__":
    test_preprocess_last_user_message()