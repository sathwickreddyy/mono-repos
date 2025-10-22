from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator


class TaskCreateRequest(BaseModel):
    """
    Request model for creating a new task.
    
    Supports multiple financial calculation types:
    - VaR calculations (portfolio data)
    - Monte Carlo pricing (option params)
    - Portfolio optimization (assets, returns)
    - Simple calculations (amount-based)
    """
    
    data: Dict[str, Any] = Field(
        ...,
        description="Task input data for financial calculation",
        examples=[
            {
                "portfolio": {
                    "positions": [
                        {"symbol": "AAPL", "quantity": 100, "price": 150.0}
                    ],
                    "volatilities": {"AAPL": 0.25}
                },
                "confidence_level": 0.95,
                "time_horizon": 10
            }
        ]
    )
    
    priority: str = Field(
        default="medium",
        description="Task priority level",
        pattern="^(high|medium|low)$",
        examples=["high"]
    )
    
    queue: Optional[str] = Field(
        default=None,
        description="Target queue name (auto-assigned if not specified)",
        max_length=50
    )
    
    @field_validator("data", mode="before")
    @classmethod
    def validate_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task data - accept any dict for flexibility."""
        if not isinstance(v, dict):
            raise ValueError("Task data must be a dictionary")
        return v

        
        # Generate JSON schema for OpenAPI docs
        schema_extra = {
            "example": {
                "data": {
                    "amount": 10000.00,
                    "rate": 0.05,
                    "periods": 12,
                    "calculation_type": "compound_interest"
                },
                "priority": "high"
            }
        }


class TaskQueryParams(BaseModel):
    """
    Query parameters for listing tasks.
    
    Used for filtering and pagination in task list endpoint.
    
    Attributes:
        status: Filter by task status
        priority: Filter by priority
        limit: Maximum results to return
        offset: Number of results to skip
    """
    
    status: Optional[str] = Field(
        default=None,
        description="Filter by task status",
        pattern="^(PENDING|STARTED|SUCCESS|FAILURE|RETRY)$",
    )
    
    priority: Optional[str] = Field(
        default=None,
        description="Filter by priority",
        pattern="^(high|medium|low)$",
    )
    
    limit: int = Field(
        default=100,
        description="Maximum results to return",
        ge=1,
        le=1000,
    )
    
    offset: int = Field(
        default=0,
        description="Number of results to skip",
        ge=0,
    )
    
    class Config:
        """Pydantic model configuration."""
        
        schema_extra = {
            "example": {
                "status": "SUCCESS",
                "priority": "high",
                "limit": 50,
                "offset": 0
            }
        }
