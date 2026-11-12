provider "aws" {
  region  = "us-east-2"
  profile = "rota-livre"

  default_tags {
    tags = {
      Project     = "ROTA-LIVRE"
      Environment = "academic"
      ManagedBy   = "Terraform"
      Institution = "FIAP"
    }
  }
}
