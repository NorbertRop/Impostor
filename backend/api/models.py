from pydantic import BaseModel

class CreateRoomRequest(BaseModel):
    user_id: str
    username: str
    source: str = 'api'

class JoinRoomRequest(BaseModel):
    user_id: str
    username: str
    source: str = 'api'

class StartGameRequest(BaseModel):
    host_uid: str

