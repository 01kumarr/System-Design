from fastapi import Request
import hashlib
from typing import Optional

class ClientIndetifier:
    @staticmethod
    def get_client_ip(request: Request) -> str:
        '''Extracts the client's IP address from the request
        '''
        forwarded_for = request.headers.get('x-forwarded-For')
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        ## check for real ip
        real_ip = request.headers.get('x-real-IP')
        if real_ip:
            return real_ip.strip()
        
        return request.client.host # type: ignore
    
    @staticmethod
    def generate_key(request: Request, user_id: Optional[str] = None) -> str:
        '''Generates a unique key for rate limiting based on the request and user ID
        '''
        if user_id:
            return f"user:{user_id}"
        
        client_ip = ClientIndetifier.get_client_ip(request)
        return f"ip:{client_ip}"
    
    @staticmethod
    def hash_key(key: str) -> str:
        "Generate a hash of the key for logging purposes"
        return hashlib.md5(key.encode()).hexdigest()[:8] 
    

