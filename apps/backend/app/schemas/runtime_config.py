from pydantic import BaseModel, Field


class RuntimeConfigItem(BaseModel):
    scope: str = Field(pattern="^(solve|classify)$")
    vendor: str
    base_url: str
    api_key: str
    model_name: str


class RuntimeConfigUpdateItem(BaseModel):
    vendor: str = Field(min_length=1, max_length=64)
    base_url: str = Field(min_length=1, max_length=512)
    api_key: str = Field(min_length=1, max_length=512)
    model_name: str = Field(min_length=1, max_length=128)


class RuntimeConfigUpdateRequest(BaseModel):
    solve: RuntimeConfigUpdateItem
    classify: RuntimeConfigUpdateItem


class RuntimeConfigResponse(BaseModel):
    solve: RuntimeConfigItem
    classify: RuntimeConfigItem
