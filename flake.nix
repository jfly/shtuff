{
  description = "Let's make shtuff available for nix!";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      treefmt-nix,
    }:

    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      treefmt = treefmt-nix.lib.evalModule pkgs ./nix/treefmt.nix;
    in
    {
      formatter.x86_64-linux = treefmt.config.build.wrapper;
      checks.x86_64-linux = {
        formatting = treefmt.config.build.check self;
        build = self.packages.x86_64-linux.default;
      };

      packages.x86_64-linux.default = pkgs.callPackage ./nix { };
    };
}
