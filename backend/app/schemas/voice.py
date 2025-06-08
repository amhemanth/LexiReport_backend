from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class VoiceCommandCreate(BaseModel):
    command_text: str
    # In the future, add support for audio input

class VoiceCommandResponse(BaseModel):
    id: str
    user_id: str
    command_text: str
    action_type: str
    status: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 