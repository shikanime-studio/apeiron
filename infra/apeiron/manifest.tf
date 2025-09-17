resource "kubernetes_namespace" "infinity_horizons" {
  metadata {
    name = "shikanime-studio"
  }
}

resource "kubernetes_secret" "apeiron" {
  metadata {
    name      = "apeiron"
    namespace = kubernetes_namespace.infinity_horizons.metadata[0].name
  }
  data = {
    discord_token     = var.apeiron.discord_token
    google_ai_api_key = var.apeiron.google_ai_api_key
    mistral_api_key   = var.apeiron.mistral_api_key
  }
  type = "Opaque"
}
