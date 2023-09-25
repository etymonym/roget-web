{
    description = "A minimal flake for furnishing a Python Django development environment.";
    
    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = { self, nixpkgs, flake-utils }:
        flake-utils.lib.eachDefaultSystem (system:
            let pkgs = nixpkgs.legacyPackages.${system};
            in {
                devShell = pkgs.mkShell { 
                    buildInputs = [ 
                        pkgs.python311
                        pkgs.python311Packages.django

                    ]; 
                };
            });
}