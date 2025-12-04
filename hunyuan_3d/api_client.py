"""
Tencent Cloud API Client for Hunyuan 3D Global - Using CommonClient
Supports Tencent Hunyuan 3D Global (Professional) API
"""

import asyncio
import logging
import aiohttp
from typing import Dict, Any, Optional
from tencentcloud.common.common_client import CommonClient
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TencentCloudAPIClient:
    """
    Tencent Cloud Hunyuan 3D Global API client
    Uses CommonClient for Global API access
    """
    
    def __init__(self, secret_id: str, secret_key: str, region: str = "ap-singapore"):
        """
        Initialize the Global API client
        
        Args:
            secret_id: Tencent Cloud Secret ID
            secret_key: Tencent Cloud Secret Key  
            region: API region (default: ap-singapore, only supported region for Global)
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        
        # Create credential
        cred = credential.Credential(secret_id, secret_key)
        
        # Configure HTTP profile with Global endpoint
        httpProfile = HttpProfile()
        httpProfile.endpoint = "hunyuan.intl.tencentcloudapi.com"
        
        # Create client profile
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        
        # Create common client for Hunyuan Global API
        # Service: "hunyuan", Version: "2023-09-01"
        self.client = CommonClient(
            "hunyuan",
            "2023-09-01",
            cred,
            region,
            profile=clientProfile
        )
        
        logger.info(f"Initialized Tencent Cloud Hunyuan 3D Global client for region: {region}")
        
    async def text_to_3d(self, prompt: str, enable_pbr: bool = False, face_count: int = 500000, 
                        generate_type: str = "Normal", polygon_type: str = "triangle") -> str:
        """
        Generate 3D model from text prompt
        
        Args:
            prompt: Text description for 3D model generation
            enable_pbr: Enable PBR material generation (default: False)
            face_count: Number of faces in generated model, 40000-1500000 (default: 500000)
            generate_type: Generation type - Normal/LowPoly/Geometry/Sketch (default: Normal)
            polygon_type: Polygon type for LowPoly - triangle/quadrilateral (default: triangle)
            
        Returns:
            Job ID string
        """
        try:
            logger.info(f"Starting text-to-3D generation for prompt: {prompt}")
            logger.info(f"Settings: PBR={enable_pbr}, Faces={face_count}, Type={generate_type}")
            
            # Prepare parameters
            params = {
                "Prompt": prompt,
                "EnablePBR": enable_pbr,
                "FaceCount": face_count,
                "GenerateType": generate_type
            }
            
            # Add polygon type only for LowPoly mode
            if generate_type == "LowPoly":
                params["PolygonType"] = polygon_type
            
            # Submit job (sync call, wrap in executor for async)
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None, 
                self.client.call_json,
                "SubmitHunyuanTo3DProJob",
                params
            )
            
            job_id = resp["Response"]["JobId"]
            logger.info(f"Text-to-3D job submitted successfully. JobId: {job_id}")
            return job_id
            
        except TencentCloudSDKException as e:
            error_msg = self._format_error(e)
            logger.error(f"Tencent Cloud SDK Error: {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error submitting text-to-3D job: {e}")
            raise
        
    async def image_to_3d(self, image_data: str, enable_pbr: bool = False, face_count: int = 500000,
                         generate_type: str = "Normal", polygon_type: str = "triangle") -> str:
        """
        Generate 3D model from image
        
        Args:
            image_data: Base64 encoded image data
            enable_pbr: Enable PBR material generation (default: False)
            face_count: Number of faces in generated model, 40000-1500000 (default: 500000)
            generate_type: Generation type - Normal/LowPoly/Geometry/Sketch (default: Normal)
            polygon_type: Polygon type for LowPoly - triangle/quadrilateral (default: triangle)
            
        Returns:
            Job ID string
        """
        try:
            logger.info("Starting image-to-3D generation")
            logger.info(f"Settings: PBR={enable_pbr}, Faces={face_count}, Type={generate_type}")
            
            # Prepare parameters
            params = {
                "ImageBase64": image_data,
                "EnablePBR": enable_pbr,
                "FaceCount": face_count,
                "GenerateType": generate_type
            }
            
            # Add polygon type only for LowPoly mode
            if generate_type == "LowPoly":
                params["PolygonType"] = polygon_type
            
            # Submit job (sync call, wrap in executor for async)
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None,
                self.client.call_json,
                "SubmitHunyuanTo3DProJob",
                params
            )
            
            job_id = resp["Response"]["JobId"]
            logger.info(f"Image-to-3D job submitted successfully. JobId: {job_id}")
            return job_id
            
        except TencentCloudSDKException as e:
            error_msg = self._format_error(e)
            logger.error(f"Tencent Cloud SDK Error: {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error submitting image-to-3D job: {e}")
            raise
        
    async def query_task_status(self, job_id: str) -> Dict[str, Any]:
        """
        Query the status of a task
        
        Args:
            job_id: Job ID to query
            
        Returns:
            Dictionary containing:
            - status: WAIT, RUN, FAIL, or DONE
            - result_urls: List of result file URLs (if DONE)
            - error_code: Error code (if FAIL)
            - error_message: Error message (if FAIL)
        """
        try:
            logger.info(f"Querying task status for JobId: {job_id}")
            
            # Prepare parameters
            params = {
                "JobId": job_id
            }
            
            # Query job (sync call, wrap in executor for async)
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None,
                self.client.call_json,
                "QueryHunyuanTo3DProJob",
                params
            )
            
            response = resp["Response"]
            status = response.get("Status", "")
            
            result = {
                "status": status,
                "result_urls": [],
                "error_code": response.get("ErrorCode", ""),
                "error_message": response.get("ErrorMessage", "")
            }
            
            # Extract result URLs if available
            if status == "DONE" and "ResultFile3Ds" in response:
                for file_info in response["ResultFile3Ds"]:
                    result["result_urls"].append({
                        "url": file_info.get("Url", ""),
                        "type": file_info.get("Type", ""),
                        "preview_url": file_info.get("PreviewImageUrl", "")
                    })
            
            logger.info(f"Task status: {status}")
            return result
            
        except TencentCloudSDKException as e:
            logger.error(f"Tencent Cloud SDK Error: [{e.code}] {e.message}")
            raise Exception(f"API error {e.code}: {e.message}")
        except Exception as e:
            logger.error(f"Error querying task status: {e}")
            raise
        
    async def wait_for_task_completion(self, job_id: str, max_wait_time: int = 300, poll_interval: int = 5, progress_callback=None) -> Dict[str, Any]:
        """
        Wait for a task to complete
        
        Args:
            job_id: Job ID to wait for
            max_wait_time: Maximum time to wait in seconds (default: 300)
            poll_interval: Polling interval in seconds (default: 5)
            progress_callback: Optional callback function(progress_percent, status_msg)
            
        Returns:
            Task result dictionary
        """
        logger.info(f"Waiting for task completion. JobId: {job_id}")
        
        elapsed_time = 0
        started_running = False
        run_start_time = 0
        
        while elapsed_time < max_wait_time:
            result = await self.query_task_status(job_id)
            status = result["status"]
            
            # Calculate estimated progress
            if status == "WAIT":
                progress = min(10, (elapsed_time / max_wait_time) * 10)
                status_msg = f"⏳ Kuyrukta bekliyor... ({int(progress)}%)"
            elif status == "RUN":
                if not started_running:
                    started_running = True
                    run_start_time = elapsed_time
                # Estimate: 10% queue, 90% processing (typical 3D generation takes 120-180s)
                run_time = elapsed_time - run_start_time
                estimated_total = 150  # Average generation time
                progress = 10 + min(85, (run_time / estimated_total) * 85)
                status_msg = f"🔄 3D model oluşturuluyor... ({int(progress)}%)"
            else:
                progress = 95
                status_msg = f"⚙️ İşleniyor... ({int(progress)}%)"
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(progress, status_msg)
            
            if status == "DONE":
                if progress_callback:
                    progress_callback(100, "✅ Tamamlandı!")
                logger.info(f"Task completed successfully after {elapsed_time} seconds")
                return result
            elif status == "FAIL":
                error_msg = f"Task failed: {result['error_code']} - {result['error_message']}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Still waiting or running
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval
            logger.info(f"Task status: {status}, elapsed time: {elapsed_time}s")
        
        raise Exception(f"Task did not complete within {max_wait_time} seconds")
        
    async def download_model(self, url: str, output_path: str) -> str:
        """
        Download the generated 3D model
        
        Args:
            url: Download URL
            output_path: Local path to save the model
            
        Returns:
            Path to the downloaded file
        """
        try:
            logger.info(f"Downloading model from {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        logger.info(f"Model downloaded successfully to {output_path}")
                        return output_path
                    else:
                        raise Exception(f"Failed to download model: HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            raise
    
    def _format_error(self, e: TencentCloudSDKException) -> str:
        """Format Tencent Cloud error with helpful information"""
        error_code = e.code
        error_message = e.message
        
        # Common error explanations
        error_hints = {
            "ResourceInsufficient": """
❌ KAYNAK YETERSİZ (ResourceInsufficient)

Olası Nedenler:
1. 🔴 Hesap Kotası Doldu
   - Günlük/aylık ücretsiz kota tükendi
   - Çözüm: Tencent Cloud Console'dan kotanızı kontrol edin
   
2. 💰 Yetersiz Bakiye
   - API ücretli ve hesapta yeterli kredi yok
   - Çözüm: Hesabınıza bakiye yükleyin
   
3. 🔒 API Erişim Kısıtlaması
   - Global API (Hunyuan 3D Pro) erişiminiz aktif değil
   - Çözüm: Tencent Cloud'dan API'yi aktifleştirin
   
4. 📊 Eş Zamanlı İstek Limiti
   - Çok fazla eş zamanlı istek gönderildi
   - Çözüm: Biraz bekleyip tekrar deneyin

Kontrol Edin:
- https://console.intl.cloud.tencent.com/ (Global Console)
- Billing & Cost Management
- API Gateway -> Hunyuan 3D Services
""",
            "AuthFailure": """
❌ KİMLİK DOĞRULAMA HATASI (AuthFailure)

Çözüm:
- Secret ID ve Secret Key'i kontrol edin
- Kimlik bilgilerinin Global API için olduğundan emin olun
""",
            "LimitExceeded": """
❌ LİMİT AŞILDI (LimitExceeded)

Çözüm:
- API çağrı limiti aşıldı
- Birkaç dakika bekleyip tekrar deneyin
""",
            "InvalidParameter": """
❌ GEÇERSİZ PARAMETRE (InvalidParameter)

Çözüm:
- Gönderilen parametreleri kontrol edin
- face_count: 40000-1500000 arasında olmalı
- generate_type: Normal/LowPoly/Geometry/Sketch
"""
        }
        
        hint = error_hints.get(error_code, "")
        return f"[{error_code}] {error_message}\n{hint}"
