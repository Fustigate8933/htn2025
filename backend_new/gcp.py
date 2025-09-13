import os
import json
from google.cloud import storage
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError, TransportError

class GCSClient:
    def __init__(self, bucket_name=None):
        # 如果没传 bucket_name，就从环境变量读取
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET")
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET environment variable is required")
        
        try:
            # 初始化客户端
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            # 检查bucket是否存在
            if not self.bucket.exists():
                raise ValueError(f"Bucket {self.bucket_name} does not exist")
            print(f"✅ GCS客户端初始化成功，使用存储桶: {self.bucket_name}")
            
        except DefaultCredentialsError:
            raise Exception("GCP认证失败。请设置GOOGLE_APPLICATION_CREDENTIALS环境变量")

    def upload_file(self, local_path, dest_path):
        """上传文件到 GCS"""
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"本地文件不存在: {local_path}")
            
        blob = self.bucket.blob(dest_path)
        blob.upload_from_filename(local_path)
        print(f"✅ 文件上传成功: {dest_path}")
        return f"gs://{self.bucket_name}/{dest_path}"

    def download_file(self, blob_name, local_path):
        """从 GCS 下载文件"""
        # 确保本地目录存在
        os.makedirs(os.path.dirname(local_path) if os.path.dirname(local_path) else '.', exist_ok=True)
        
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(local_path)
        print(f"✅ 文件下载成功: {local_path}")

    def generate_signed_url(self, blob_name, expiration=3600):
        """生成带签名的 URL，默认 1 小时有效"""
        blob = self.bucket.blob(blob_name)
        if not blob.exists():
            raise ValueError(f"文件不存在: {blob_name}")
        url = blob.generate_signed_url(expiration=expiration)
        return url

    def list_files(self, prefix=""):
        """列出存储桶中的文件"""
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        return [blob.name for blob in blobs]

    def delete_file(self, blob_name):
        """删除文件"""
        blob = self.bucket.blob(blob_name)
        if blob.exists():
            blob.delete()
            print(f"✅ 文件删除成功: {blob_name}")
        else:
            print(f"⚠️  文件不存在: {blob_name}")

    
    def test_gcp_credentials():
        """测试GCP认证和环境变量配置"""
        
        print("🔍 开始测试GCP认证配置...")
        print(f"项目ID: {os.getenv('GCP_PROJECT_ID', '未设置')}")
        print(f"存储桶: {os.getenv('GCS_BUCKET', '未设置')}")
        print(f"认证文件: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '未设置')}")
        
        # 检查环境变量是否设置
        if not all([os.getenv('GCP_PROJECT_ID'), os.getenv('GCS_BUCKET'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS')]):
            print("❌ 环境变量未完全设置")
            return False
        
        # 检查JSON文件是否存在
        creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not os.path.exists(creds_file):
            print(f"❌ JSON密钥文件不存在: {creds_file}")
            return False
        
        # 检查JSON文件格式
        try:
            with open(creds_file, 'r') as f:
                creds_data = json.load(f)
            
            required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            for key in required_keys:
                if key not in creds_data:
                    print(f"❌ JSON文件缺少必要键: {key}")
                    return False
            
            print(f"✅ JSON文件格式正确")
            print(f"   服务账号: {creds_data['client_email']}")
            print(f"   项目ID: {creds_data['project_id']}")
            
        except json.JSONDecodeError:
            print("❌ JSON文件格式错误")
            return False
        
        # 测试认证是否有效
        try:
            credentials = service_account.Credentials.from_service_account_file(
                creds_file,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # 初始化存储客户端
            client = storage.Client(credentials=credentials, project=os.getenv('GCP_PROJECT_ID'))
            
            # 测试列出存储桶（简单权限测试）
            buckets = list(client.list_buckets(max_results=1))
            print("✅ GCP认证成功")
            
            # 测试特定存储桶访问
            bucket_name = os.getenv('GCS_BUCKET')
            bucket = client.bucket(bucket_name)
            
            if bucket.exists():
                print(f"✅ 存储桶访问正常: {bucket_name}")
                
                # 测试上传权限
                test_blob = bucket.blob("test_permission.txt")
                test_blob.upload_from_string("权限测试文件内容")
                print("✅ 存储桶写入权限正常")
                
                # 清理测试文件
                test_blob.delete()
                print("✅ 存储桶删除权限正常")
                
                return True
            else:
                print(f"❌ 存储桶不存在或无访问权限: {bucket_name}")
                return False
                
        except DefaultCredentialsError as e:
            print(f"❌ 认证失败: {e}")
            return False
        except TransportError as e:
            print(f"❌ 网络连接错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False
    
    def test_project_match():
        """测试环境变量项目ID与JSON文件中的是否匹配"""
        
        gcp_project_id = os.getenv('GCP_PROJECT_ID')
        creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not gcp_project_id or not creds_file:
            return False
        
        try:
            with open(creds_file, 'r') as f:
                creds_data = json.load(f)
            
            json_project_id = creds_data.get('project_id', '')
            
            if gcp_project_id == json_project_id:
                print(f"✅ 项目ID匹配: {gcp_project_id}")
                return True
            else:
                print(f"❌ 项目ID不匹配: 环境变量={gcp_project_id}, JSON文件={json_project_id}")
                return False
                
        except Exception as e:
            print(f"❌ 检查项目ID时出错: {e}")
            return False