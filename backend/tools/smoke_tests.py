import os
import argparse
from dotenv import load_dotenv

from backend.services.generate_speech import generate_speech
from backend.utils.gcp import GCSClient

load_dotenv()

def test_cohere():
    """调用 Cohere 生成一段短文案，验证 COHERE_API_KEY 是否可用"""
    prompt = "Give 3 common solutions for deadlocks in database systems. 100 words max."
    text = generate_speech(prompt, style="concise", max_tokens=120)
    if not text:
        print("❌ Cohere 生成失败，请检查 COHERE_API_KEY")
        return False
    print("✅ Cohere 正常，示例输出：\n", text)
    return True

def test_gcs_basic():
    """基础测试：创建文件 -> 上传到 GCS -> 列表 -> 清理本地文件"""
    try:
        print("🔄 初始化GCS客户端...")
        gcs = GCSClient()

        # 1) 创建测试文件
        test_file = "gcs_test_file.txt"
        test_content = (
            "这是一个GCS存储测试文件\n"
            "内容: Hello Google Cloud Storage!\n"
        )
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        print(f"✅ 本地测试文件创建: {test_file}")

        # 2) 上传
        blob_name = "test_uploads/gcs_test_file.txt"
        gcs_path = gcs.upload_file(test_file, blob_name)
        print(f"✅ 已上传: {gcs_path}")

        # 3) 列出
        files = gcs.list_files("test_uploads/")
        print("📂 test_uploads/ 下文件：", files)

        # 4) 生成 1 小时签名URL
        url = gcs.generate_signed_url(blob_name, expiration=3600)
        print("🔗 临时访问链接：", url)

        # 5) 清理本地
        os.remove(test_file)
        print(f"🧹 已删除本地文件: {test_file}")
        print("🎉 GCS 基础链路 OK")
        return True
    except Exception as e:
        print("❌ GCS 基础测试失败：", e)
        # 确保清理本地文件
        if os.path.exists("gcs_test_file.txt"):
            os.remove("gcs_test_file.txt")
        return False

def test_json_and_id():
    """检查 GCP 环境变量 + JSON 密钥 + 项目ID 是否匹配"""
    ok1 = GCSClient.test_gcp_credentials()
    print("\n" + "="*50 + "\n")
    ok2 = GCSClient.test_project_match()
    print("\n" + "="*50 + "\n")

    if ok1 and ok2:
        print("🎉 所有测试通过！GCP 配置正确。")
        return True
    else:
        print("❌ 测试失败：请检查环境变量/密钥文件/权限/网络。")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hack-the-Stage 后端冒烟测试脚本")
    parser.add_argument("--cohere", action="store_true", help="测试 Cohere 生成")
    parser.add_argument("--gcs", action="store_true", help="测试 GCS 上传/列表/签名URL")
    parser.add_argument("--gcpconf", action="store_true", help="测试 GCP 凭证与项目ID匹配")
    args = parser.parse_args()

    ran = False
    if args.cohere:
        ran = True
        test_cohere()
    if args.gcs:
        ran = True
        test_gcs_basic()
    if args.gcpconf:
        ran = True
        test_json_and_id()

    if not ran:
        # 默认全部跑
        test_cohere()
        print("\n" + "="*60 + "\n")
        test_gcs_basic()
        print("\n" + "="*60 + "\n")
        test_json_and_id()
