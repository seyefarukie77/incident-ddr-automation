variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "europe-west2"
}

variable "service_name" {
  type    = string
  default = "incident-ddr-api"
}

variable "image" {
  type = string
}