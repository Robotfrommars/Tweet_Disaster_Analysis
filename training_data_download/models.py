

from pydantic import BaseModel, Field
from typing import List

class BlueskyPost(BaseModel):
	_id: str
	post_id: str
	createdAt: str
	text: str
	disaster_type: str