{
  inputs = {
    devenv.url = "github:cachix/devenv";
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  nixConfig = {
    extra-public-keys = [
      "shikanime.cachix.org-1:OrpjVTH6RzYf2R97IqcTWdLRejF6+XbpFNNZJxKG8Ts="
      "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw="
    ];
    extra-substituters = [
      "https://shikanime.cachix.org"
      "https://devenv.cachix.org"
    ];
  };

  outputs =
    inputs@{
      devenv,
      flake-parts,
      treefmt-nix,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        devenv.flakeModule
        treefmt-nix.flakeModule
      ];
      perSystem =
        { pkgs, ... }:
        let
          google-cloud-sdk = pkgs.google-cloud-sdk.withExtraComponents [
            pkgs.google-cloud-sdk.components.alpha
            pkgs.google-cloud-sdk.components.beta
            pkgs.google-cloud-sdk.components.cloud-run-proxy
            pkgs.google-cloud-sdk.components.log-streaming
          ];
        in
        {
          treefmt = {
            projectRootFile = "flake.nix";
            enableDefaultExcludes = true;
            programs = {
              dockfmt.enable = true;
              hclfmt.enable = true;
              nixfmt.enable = true;
              prettier.enable = true;
              ruff-format.enable = true;
              shfmt.enable = true;
              statix.enable = true;
              taplo.enable = true;
              terraform.enable = true;
            };
            settings.global.excludes = [
              "*.terraform.lock.hcl"
              "LICENSE"
            ];
          };
          devenv.shells.default = {
            containers = pkgs.lib.mkForce { };
            languages = {
              opentofu.enable = true;
              nix.enable = true;
            };
            languages.python = {
              enable = true;
              uv = {
                enable = true;
                sync.enable = true;
              };
              venv.enable = true;
            };
            cachix = {
              enable = true;
              push = "shikanime";
            };
            git-hooks.hooks = {
              actionlint.enable = true;
              deadnix.enable = true;
              flake-checker.enable = true;
              shellcheck.enable = true;
              tflint.enable = true;
            };
            packages = [
              google-cloud-sdk
              pkgs.gh
              pkgs.kubectl
              pkgs.kustomize
              pkgs.skaffold
              pkgs.sops
              pkgs.uv
              pkgs.yq
            ];
          };
        };
      systems = [
        "x86_64-linux"
        "x86_64-darwin"
        "aarch64-linux"
        "aarch64-darwin"
      ];
    };
}
