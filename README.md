# Roget-Web
A generalized thesaurus; query and visualize relations between words / phrases.

## Usage
This project is currently a WIP and so unable to be used effectively -- check back soon for that to change though!

That being said, a [nix flake](flake.nix) is included in the repo which will furnish a `dev-shell` -- in response to running `nix develop` ( given you have [Nix](https://nixos.org/) w/ [flakes](https://nixos.wiki/wiki/Flakes) enabled ) -- with the necessary packages for running / interacting with the project locally in its current state. Additionally you will need to run `nix run .#init_pg` which will take care of configuring a local PostgreSQL database cluster + server + db for interacting with `Roget-Web`.

## Acknowledgements

- The name of `Roget-Web` is an eponymous reference to [Peter Mark Roget](https://en.wikipedia.org/wiki/Peter_Mark_Roget) who is responsible for originally publishing the *Thesaurus of English Words and Phrases* in 1852, more commonly known as [*Roget's Thesaurus*](https://en.wikipedia.org/wiki/Roget%27s_Thesaurus).

- The majority of [`.gitignore`](.gitignore) are sourced from the [official Github repository for `.gitignore` templates](https://github.com/github/gitignore).

## License
This repository and any of its original contents are licensed under [MPL 2.0](LICENSE.txt).

This project is built using Django which is licensed under [BSD 3-Clause](LICENSE_DJANGO.txt).
