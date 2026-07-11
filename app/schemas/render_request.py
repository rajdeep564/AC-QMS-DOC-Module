"""Discriminated render request union for POST /render."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.schemas.aws_render import AwsRenderInput
from app.schemas.coa_render import CoaRenderInput


class InlineCoaRenderRequest(BaseModel):
    document_type: Literal["coa"]
    payload: CoaRenderInput


class InlineAwsRenderRequest(BaseModel):
    document_type: Literal["aws"]
    payload: AwsRenderInput


RenderRequest = Annotated[
    InlineCoaRenderRequest | InlineAwsRenderRequest,
    Field(discriminator="document_type"),
]
