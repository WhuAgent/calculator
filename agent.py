from agent_network.base import BaseAgent
from agent_network.exceptions import ReportError


class calculator(BaseAgent):
    def __init__(self, graph, config, logger):
        super().__init__(graph, config, logger)

    def forward(self, messages, **kwargs):
        calc_task = kwargs.get("task")
        if not calc_task:
            print("calculation_task is not provided")

        prompt = f"""
        请为以下数学问题生成Python解题代码：
        {calc_task}
        
        要求：
        1. 只返回可执行的Python代码，且已经执行过"import math"，请不要重复导入
        2. 只能使用math模块进行数学计算，禁止import其他库
        3. 将最终结果赋值给变量result
        4. 只需要文本格式的python代码，不要包含任何解释或Markdown格式
        """
        self.add_message("user", prompt, messages)
        response = self.chat_llm(messages,
                                 api_key="sk-cf690968fd414e058f7cb0d2d3273c22",
                                 base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                                 model="qwen2.5-32b-instruct"
                                 )
        response_data = response.content

        print(response_data)

        self.log("assistant", response_data)

        # 可能会包含markdown格式，进行提取
        import re
        code_pattern = r'(?s)(?:```python\n)?(.*?)(?:```)?\Z'
        math_module_pattern = r''
        match = re.search(code_pattern, response_data, re.MULTILINE)
        code =  match.group(1).strip() if match else response_data

        # 创建安全环境
        restricted_env = {
            '__builtins__': {
                'print': print,
                'range': range,
                'list': list,
                'dict': dict,
                'str': str,
                'float': float,
                'int': int,
                'round': round  # 允许使用 round
            },
            'math': __import__('math'),
            'result': None
        }

        answer = None
        try:
            # 语法检查
            import ast
            ast.parse(code)
            # 执行代码
            exec(code, restricted_env)
            answer = restricted_env['result']
        except Exception as e:
            print( f"执行错误: {str(e)}")
            answer = "fail, please try again"


        result_str = f"""###calc_task###\n {calc_task}\n \n ###calculation_result###\n {answer}"""

        result = {
            "result": result_str
        }
        return result