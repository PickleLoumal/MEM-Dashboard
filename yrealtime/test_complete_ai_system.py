#!/usr/bin/env python3
"""
AI经济分析师智能对话系统
支持用户与AI经济专家进行实时经济分析对话
"""

import os
import sys
import django
import json
from datetime import datetime

# 设置Django环境
project_root = os.path.dirname(os.path.abspath(__file__))
django_api_path = os.path.join(project_root, 'src', 'django_api')
sys.path.insert(0, project_root)
sys.path.insert(0, django_api_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')

try:
    django.setup()
    print("✅ Django环境初始化成功")
except Exception as e:
    print(f"❌ Django环境初始化失败: {e}")
    sys.exit(1)

from ai_chat.data_analyzer import enhance_ai_prompt_with_data
import requests

class AIEconomicChatSystem:
    """AI经济分析师智能对话系统"""
    
    def __init__(self):
        self.conversation_history = []
        self.session_start_time = datetime.now()
        
        self.ai_config = {
            'api_key': os.getenv('GROK_API_KEY'),
            'api_base_url': os.getenv('GROK_API_BASE_URL', 'https://api.x.ai/v1'),
            'model': 'grok-3',
            'max_tokens': 2000,
            'temperature': 0.7
        }
        
        self.quick_questions = [
            "分析当前美国通胀趋势和美联储政策的关系",
            "就业市场与经济增长的相关性分析",
            "货币供应量对通胀的影响机制",
            "房地产市场与利率政策的关联性",
            "贸易逆差对美国经济的长期影响",
            "银行信贷与经济周期的关系分析",
            "政府债务可持续性评估",
            "金融稳定性风险因素分析"
        ]
    
    def optimize_prompt_length(self, prompt: str, max_chars: int = 8000) -> str:
        """优化提示词长度，确保在token限制内"""
        if len(prompt) <= max_chars:
            return prompt
        
        print(f"⚠️ 提示词过长 ({len(prompt)} 字符)，正在优化...")
        
        # 分割提示词各部分
        lines = prompt.split('\n')
        
        # 保留核心部分
        essential_parts = []
        data_parts = []
        
        in_data_section = False
        for line in lines:
            if '**经济数据：**' in line or '=== 核心经济数据 ===' in line:
                in_data_section = True
                essential_parts.append(line)
            elif '**分析要求：**' in line:
                in_data_section = False
                essential_parts.append(line)
            elif in_data_section:
                data_parts.append(line)
            else:
                essential_parts.append(line)
        
        # 如果数据部分太长，进一步压缩
        if len('\n'.join(essential_parts + data_parts)) > max_chars:
            # 只保留最重要的数据行（包含数值的行）
            important_data = [line for line in data_parts if ':' in line and any(c.isdigit() for c in line)]
            data_parts = important_data[:15]  # 最多15行数据
        
        optimized_prompt = '\n'.join(essential_parts + data_parts)
        print(f"✅ 提示词已优化至 {len(optimized_prompt)} 字符")
        return optimized_prompt

    def call_grok_api(self, prompt: str) -> str:
        """调用Grok API获取AI回答"""
        if not self.ai_config['api_key']:
            return "API密钥未配置，跳过AI调用"
        
        # 优化提示词长度
        optimized_prompt = self.optimize_prompt_length(prompt)
        
        try:
            headers = {
                'Authorization': f"Bearer {self.ai_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.ai_config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是一位专业的经济分析师，请基于提供的真实经济数据进行精简而专业的分析。'},
                    {'role': 'user', 'content': optimized_prompt}
                ],
                'max_tokens': self.ai_config['max_tokens'],
                'temperature': self.ai_config['temperature']
            }
            
            print(f"🌐 正在调用Grok API ({self.ai_config['model']})...")
            print(f"📏 提示词长度: {len(optimized_prompt)} 字符")
            
            response = requests.post(
                f"{self.ai_config['api_base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=90  # 减少超时时间
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    print("✅ Grok API调用成功")
                    return content
                else:
                    print(f"❌ Grok API响应格式异常: {result}")
                    return f"API响应格式异常: {result}"
            else:
                print(f"❌ Grok API错误: {response.status_code} - {response.text}")
                return f"API错误: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            print("❌ Grok API调用超时")
            return "API调用超时"
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误: {e}")
            return f"连接错误: {e}"
        except Exception as e:
            print(f"❌ Grok API调用异常: {e}")
            return f"API调用异常: {e}"
    
    def display_welcome_banner(self):
        """显示欢迎界面"""
        print("="*80)
        print("🤖 AI经济分析师智能对话系统")
        print("="*80)
        print("功能特点:")
        print("• 🧠 AI智能指标发现 - 自动选择最相关的经济指标")
        print("• 📊 真实数据分析 - 基于最新经济数据进行专业分析")
        print("• 🎯 精准回答 - 聚焦用户问题提供专业洞察")
        print("• ⚡ 高效处理 - 每次分析限制5个核心指标")
        print("• 🔄 对话记录 - 保存完整的分析对话历史")
        print("="*80)
        print(f"🤖 AI配置: {self.ai_config['model']} | 温度: {self.ai_config['temperature']}")
        print(f"⏰ 会话开始时间: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    
    def display_quick_questions(self):
        """显示快速问题选项"""
        print("\n💡 快速问题 (输入编号即可):")
        for i, question in enumerate(self.quick_questions, 1):
            print(f"  {i}. {question}")
        print("\n📝 您也可以直接输入自己的经济问题...")
        print("💬 特殊命令: 'history' 查看对话历史, 'quit' 退出, 'help' 查看帮助")
    
    def get_user_input(self) -> str:
        """获取用户输入"""
        try:
            user_input = input("\n>>> ").strip()
            return user_input
        except KeyboardInterrupt:
            print("\n👋 用户中断，再见！")
            return "quit"
        except EOFError:
            return "quit"
    
    def process_user_input(self, user_input: str) -> str:
        """处理用户输入"""
        if not user_input:
            return ""
        
        # 处理特殊命令
        if user_input.lower() == 'quit':
            return 'quit'
        elif user_input.lower() == 'help':
            self.show_help()
            return ""
        elif user_input.lower() == 'history':
            self.show_conversation_history()
            return ""
        
        # 处理数字选择（快速问题）
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(self.quick_questions):
                return self.quick_questions[index]
            else:
                print(f"❌ 无效选择，请输入 1-{len(self.quick_questions)} 之间的数字")
                return ""
        
        # 直接返回用户问题
        return user_input
    
    def show_help(self):
        """显示帮助信息"""
        print("\n" + "="*60)
        print("📖 AI经济分析师使用帮助")
        print("="*60)
        print("🎯 如何使用:")
        print("  1. 直接输入经济问题，如：'分析美国当前通胀情况'")
        print("  2. 输入数字选择快速问题，如：输入 '1'")
        print("  3. 系统会自动分析并获取相关经济数据")
        print("  4. AI专家将基于真实数据提供专业分析")
        print("\n🔧 特殊命令:")
        print("  • history - 查看本次会话的对话历史")
        print("  • help - 显示此帮助信息")
        print("  • quit - 退出对话系统")
        print("\n💡 提示:")
        print("  • 问题越具体，分析越精准")
        print("  • 系统会智能选择最相关的5个经济指标")
        print("  • 每个指标提供最近10个数据点进行分析")
        print("="*60)
    
    def show_conversation_history(self):
        """显示对话历史"""
        if not self.conversation_history:
            print("\n📝 本次会话暂无对话记录")
            return
        
        print(f"\n📚 对话历史 (会话开始: {self.session_start_time.strftime('%H:%M:%S')})")
        print("="*60)
        
        for i, record in enumerate(self.conversation_history, 1):
            timestamp = record['timestamp'].strftime('%H:%M:%S')
            print(f"\n{i}. [{timestamp}] 用户问题:")
            print(f"   {record['question']}")
            
            if record['success']:
                print(f"   ✅ AI分析: {record['response'][:100]}...")
                print(f"   📊 指标数: {record.get('indicators_count', 'N/A')}")
            else:
                print(f"   ❌ 分析失败: {record.get('error', 'Unknown error')}")
        
        print("="*60)
    
    def analyze_question(self, question: str) -> dict:
        """分析用户问题并获取AI回答"""
        print(f"\n🔍 正在分析: {question}")
        print("="*60)
        
        result = {
            "question": question,
            "timestamp": datetime.now(),
            "success": False,
            "response": "",
            "error": "",
            "indicators_count": 0,
            "categories": [],
            "analysis_time": 0
        }
        
        try:
            start_time = datetime.now()
            
            # 第1步：生成AI智能增强提示词
            print("🤖 步骤1: AI智能指标发现...")
            enhanced_prompt, analysis_data = enhance_ai_prompt_with_data(
                question, 
                use_ai_discovery=True
            )
            
            # 验证数据质量
            if analysis_data and 'data_series' in analysis_data:
                total_indicators = sum(len(series_data) for series_data in analysis_data['data_series'].values())
                categories = list(analysis_data['data_series'].keys())
                
                result['indicators_count'] = total_indicators
                result['categories'] = categories
                
                print(f"✅ 数据发现成功")
                print(f"   • 指标总数: {total_indicators}")
                print(f"   • 覆盖类别: {categories}")
                print(f"   • 提示词长度: {len(enhanced_prompt)} 字符")
                
                # 验证真实数据包含 - 适配动态指标选择
                has_real_data = ("经济数据" in enhanced_prompt or "核心经济数据" in enhanced_prompt) and (
                    "【" in enhanced_prompt or  # 检查是否有分类标识
                    any(category in enhanced_prompt for category in categories) or  # 检查是否有实际类别名
                    ":" in enhanced_prompt  # 检查是否有指标:数值格式
                )
                has_statistics = "%" in enhanced_prompt or "(" in enhanced_prompt  # 检查是否有变化率等统计信息
                has_user_question = question in enhanced_prompt
                
                print(f"   • 真实数据: {'✅' if has_real_data else '❌'}")
                print(f"   • 统计分析: {'✅' if has_statistics else '❌'}")
                print(f"   • 原始问题: {'✅' if has_user_question else '❌'}")
                
                if not (has_real_data and has_user_question):
                    result['error'] = "增强提示词质量检查失败 - 缺少必要数据或问题"
                    return result
            else:
                result['error'] = "分析数据为空或格式异常"
                print("❌ 数据发现失败")
                return result
            
            # 第2步：调用AI API获取专业分析
            print("\n🤖 步骤2: 调用AI获取专业分析...")
            ai_response = self.call_grok_api(enhanced_prompt)
            
            if ai_response and not ai_response.startswith("API"):
                result['response'] = ai_response
                result['success'] = True
                
                analysis_time = (datetime.now() - start_time).total_seconds()
                result['analysis_time'] = analysis_time
                
                print(f"✅ AI分析完成 (耗时: {analysis_time:.1f}秒)")
                print(f"📏 回答长度: {len(ai_response)} 字符")
                
            else:
                result['error'] = f"AI API调用失败: {ai_response}"
                print(f"❌ AI分析失败: {ai_response}")
            
        except Exception as e:
            result['error'] = f"分析异常: {str(e)}"
            print(f"❌ 分析执行异常: {e}")
            import traceback
            traceback.print_exc()
        
        return result
    
    
    def display_ai_response(self, response: str):
        """显示AI回答"""
        print("\n" + "="*80)
        print("🤖 AI经济专家分析")
        print("="*80)
        
        # 分段显示长回答
        if len(response) > 1000:
            paragraphs = response.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                print(paragraph)
                if i < len(paragraphs) - 1:
                    print()  # 段落间空行
        else:
            print(response)
        
        print("="*80)
    
    def save_conversation_session(self):
        """保存会话记录"""
        if not self.conversation_history:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = f"ai_chat_session_{timestamp}.json"
        
        session_data = {
            "session_info": {
                "start_time": self.session_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_questions": len(self.conversation_history),
                "successful_analyses": sum(1 for r in self.conversation_history if r['success'])
            },
            "conversation_history": [
                {
                    "timestamp": record['timestamp'].isoformat(),
                    "question": record['question'],
                    "success": record['success'],
                    "response": record['response'] if record['success'] else "",
                    "error": record.get('error', ''),
                    "indicators_count": record.get('indicators_count', 0),
                    "categories": record.get('categories', []),
                    "analysis_time": record.get('analysis_time', 0)
                }
                for record in self.conversation_history
            ]
        }
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 会话记录已保存到: {session_file}")
        except Exception as e:
            print(f"⚠️ 保存会话记录失败: {e}")
    
    def start_chat(self):
        """启动对话系统"""
        self.display_welcome_banner()
        
        while True:
            self.display_quick_questions()
            
            # 获取用户输入
            user_input = self.get_user_input()
            
            # 处理输入
            question = self.process_user_input(user_input)
            
            # 退出处理
            if question == 'quit':
                print("\n👋 感谢使用AI经济分析师系统！")
                if self.conversation_history:
                    print(f"📊 本次会话共分析了 {len(self.conversation_history)} 个问题")
                    
                    save_choice = input("💾 是否保存本次会话记录? (y/n): ").strip().lower()
                    if save_choice in ['y', 'yes', '是']:
                        self.save_conversation_session()
                
                print("再见！🎯")
                break
            
            # 跳过空输入或命令处理
            if not question:
                continue
            
            # 分析问题
            print(f"\n💬 您的问题: {question}")
            result = self.analyze_question(question)
            
            # 记录到历史
            self.conversation_history.append(result)
            
            # 显示结果
            if result['success']:
                self.display_ai_response(result['response'])
                
                # 显示分析摘要
                print(f"\n📊 分析摘要:")
                print(f"   • 分析耗时: {result['analysis_time']:.1f}秒")
                print(f"   • 使用指标: {result['indicators_count']}个")
                print(f"   • 涉及类别: {', '.join(result['categories'])}")
            else:
                print(f"\n❌ 分析失败: {result['error']}")
                print("💡 建议:")
                print("   • 检查网络连接")
                print("   • 尝试重新表述问题")
                print("   • 使用更具体的经济术语")
            
            # 询问是否继续
            print(f"\n{'='*80}")
            continue_choice = input("🔄 继续提问? (直接回车继续, 输入 'quit' 退出): ").strip()
            if continue_choice.lower() in ['quit', '退出', 'q']:
                question = 'quit'
                continue


def main():
    """主函数 - 启动AI经济分析师对话系统"""
    try:
        chat_system = AIEconomicChatSystem()
        chat_system.start_chat()
        
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，系统退出")
        return True
    except Exception as e:
        print(f"❌ 系统运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
