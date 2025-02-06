
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class ModelVersion:
    def __init__(self, version_dir: str = "model_versions"):
        self.version_dir = version_dir
        os.makedirs(version_dir, exist_ok=True)
        
    def save_version(self, model_path: str, config: Dict[str, Any]) -> str:
        """Save a model version with its configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_hash = hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]
        version_id = f"{timestamp}_{config_hash}"
        
        version_path = os.path.join(self.version_dir, version_id)
        os.makedirs(version_path)
        
        # Save configuration
        with open(os.path.join(version_path, "config.json"), "w") as f:
            json.dump(config, f, indent=2)
            
        # Save model files
        for file in os.listdir(model_path):
            if file.endswith('.pt') or file.endswith('.bin'):
                src = os.path.join(model_path, file)
                dst = os.path.join(version_path, file)
                os.rename(src, dst)
                
        return version_id
    
    def load_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Load a specific model version"""
        version_path = os.path.join(self.version_dir, version_id)
        if not os.path.exists(version_path):
            return None
            
        with open(os.path.join(version_path, "config.json")) as f:
            return json.load(f)
            
    def list_versions(self) -> Dict[str, Dict[str, Any]]:
        """List all available model versions"""
        versions = {}
        for version_id in os.listdir(self.version_dir):
            config = self.load_version(version_id)
            if config:
                versions[version_id] = config
        return versions
