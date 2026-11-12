# Optional transport for AWS accounts that allow OIDC and custom SSM documents.
variable "enable_github_oidc_deploy" {
  description = "Enable GitHub OIDC and a restricted SSM deployment document."
  type        = bool
  default     = false
}

variable "github_deploy_instance_id" {
  description = "ID of the existing EC2 targeted by the optional OIDC deploy."
  type        = string
  default     = "i-054604c12c64a62e9"

  validation {
    condition     = can(regex("^i-[0-9a-f]{17}$", var.github_deploy_instance_id))
    error_message = "Use the existing EC2 instance ID."
  }
}

data "aws_caller_identity" "deploy" {
  count = var.enable_github_oidc_deploy ? 1 : 0
}

data "aws_region" "deploy" {
  count = var.enable_github_oidc_deploy ? 1 : 0
}

resource "aws_iam_openid_connect_provider" "github" {
  count          = var.enable_github_oidc_deploy ? 1 : 0
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

resource "aws_iam_role" "github_deploy" {
  count = var.enable_github_oidc_deploy ? 1 : 0
  name  = "rota-livre-github-deploy"

  # The production environment permits only the main branch in GitHub.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRoleWithWebIdentity"
      Principal = { Federated = aws_iam_openid_connect_provider.github[0].arn }
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = "repo:victoriafpizza@126582867/GlobalSolution2026@1451558137:environment:rota-livre-production"
        }
      }
    }]
  })
}

resource "aws_ssm_document" "github_deploy" {
  count           = var.enable_github_oidc_deploy ? 1 : 0
  name            = "RotaLivre-Deploy"
  document_type   = "Command"
  document_format = "JSON"

  content = jsonencode({
    schemaVersion = "2.2"
    description   = "Deploy an exact approved main commit on ROTA LIVRE."
    parameters = {
      Commit = {
        type              = "String"
        description       = "Full Git SHA from the approved workflow."
        allowedPattern    = "^[0-9a-f]{40}$"
        interpolationType = "ENV_VAR"
      }
    }
    mainSteps = [{
      action       = "aws:runShellScript"
      name         = "deploy"
      precondition = { StringEquals = ["platformType", "Linux"] }
      inputs = {
        timeoutSeconds = "1200"
        runCommand     = ["exec /usr/local/sbin/rota-livre-deploy \"$SSM_Commit\""]
      }
    }]
  })
}

resource "aws_iam_role_policy" "github_deploy" {
  count = var.enable_github_oidc_deploy ? 1 : 0
  name  = "deploy-on-existing-ec2"
  role  = aws_iam_role.github_deploy[0].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "ssm:SendCommand"
        Resource = [
          aws_ssm_document.github_deploy[0].arn,
          "arn:aws:ec2:${data.aws_region.deploy[0].region}:${data.aws_caller_identity.deploy[0].account_id}:instance/${var.github_deploy_instance_id}",
        ]
      },
      {
        # GetCommandInvocation has no resource-level authorization.
        Effect   = "Allow"
        Action   = "ssm:GetCommandInvocation"
        Resource = "*"
      },
    ]
  })
}

output "github_deploy_role_arn" {
  description = "Set AWS_DEPLOY_ROLE_ARN in GitHub when OIDC is enabled."
  value       = try(aws_iam_role.github_deploy[0].arn, null)
}
