import os
from flask import Flask 
from coherex import generate_speech
from backend.utils.gcp import GCSClient
from dotenv import load_dotenv

load_dotenv()

#Cohere 
prompt = """
Can you please common solutions for dead locks in database systems? Please limit the response to 100 words.
"""

speech_text = generate_speech(prompt, 100)
print(speech_text)

#GCP: 

def test_gcs_basic():
    """基础测试：创建文件、上传、列出文件"""
    try:
        # 初始化GCS客户端
        print("🔄 初始化GCS客户端...")
        gcs = GCSClient()
        
        # 1. 创建测试文件
        print("\n📝 创建测试文件...")
        test_file = "gcs_test_file.txt"
        test_content = """
这是一个GCS存储测试文件
创建时间: 2024年
内容: Hello Google Cloud Storage!
测试上传和列表功能。"""
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"✅ 测试文件创建成功: {test_file}")
        
        # 2. 上传文件到GCS
        print("\n📤 上传文件到GCS...")
        gcs_path = gcs.upload_file(test_file, "test_uploads/gcs_test_file.txt")
        print(f"✅ 文件上传成功!")
        print(f"   GCS路径: {gcs_path}")
        
        # 3. 列出存储桶中的文件
        print("\n📁 列出存储桶中的文件...")
        files = gcs.list_files()
        
        if files:
            print("找到以下文件:")
            for i, file in enumerate(files, 1):
                print(f"  {i}. {file}")
        else:
            print("存储桶为空")
        
        # 4. 只列出测试文件夹的文件
        print(f"\n📂 列出测试文件夹 'test_uploads/' 中的文件:")
        test_files = gcs.list_files("test_uploads/")
        
        if test_files:
            for file in test_files:
                print(f"  - {file}")
        else:
            print("  测试文件夹为空")
        
        # 5. 清理本地测试文件
        print(f"\n🧹 清理本地文件...")
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"✅ 本地测试文件已删除: {test_file}")
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f" 测试失败: {e}")
        # 确保清理本地文件
        if 'test_file' in locals() and os.path.exists(test_file):
            os.remove(test_file)

def test_json_and_id():
    success1 = GCSClient.test_gcp_credentials()
    print("\n" + "="*50 + "\n")

    success2 = GCSClient.test_project_match()
    print("\n" + "="*50 + "\n")
    if success1 and success2:
        print("🎉 所有测试通过！GCP配置正确。")
        print("\n下一步建议:")
        print("1. 你现在可以安全地使用GCS客户端了")
        print("2. 记得在正式代码中处理异常情况")
        print("3. 定期轮换密钥以提高安全性")
    else:
        print("❌ 部分测试失败，请检查配置。")
        print("\n排查建议:")
        print("1. 检查环境变量是否设置正确")
        print("2. 确认JSON密钥文件路径正确且内容完整")
        print("3. 确认服务账号有足够的GCS权限")
        print("4. 检查网络连接是否正常")


if __name__ == "__main__":
    
    #test_gcs_basic()
    test_json_and_id()
    


