import argparse
import logging
import sys
import signal
from src.application import Application
from src.utils.logging_config import setup_logging

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='小智助手')
    
    # 添加界面模式参数
    parser.add_argument(
        '--mode', 
        choices=['gui', 'cli'],
        default='gui',
        help='运行模式：gui(图形界面) 或 cli(命令行)'
    )
    
    # 添加协议选择参数
    parser.add_argument(
        '--protocol', 
        choices=['websocket', 'mqtt'], 
        default='websocket',
        help='通信协议：websocket 或 mqtt'
    )
    
    parser.add_argument('--debug', action='store_true',
                      help='启用调试模式')
    
    return parser.parse_args()

def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    logger.info("接收到中断信号，正在关闭...")
    app = Application.get_instance()
    app.shutdown()
    sys.exit(0)

def main():
    # 配置命令行参数
    parser = argparse.ArgumentParser(description='小智助手')
    parser.add_argument('--mode', choices=['gui', 'cli'], default='gui',
                      help='运行模式：gui（图形界面）或 cli（命令行）')
    parser.add_argument('--protocol', choices=['websocket', 'mqtt'], default='websocket',
                      help='通信协议：websocket 或 mqtt')
    parser.add_argument('--debug', action='store_true',
                      help='启用调试模式')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 配置日志
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 获取应用程序实例并运行
    app = Application.get_instance()
    try:
        app.run(
            mode=args.mode,
            protocol=args.protocol,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        app.shutdown()
    except Exception as e:
        print(f"程序出现错误: {e}")
        app.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main()