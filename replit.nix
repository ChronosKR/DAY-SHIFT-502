{ pkgs }:

{
  # bring in a current Python and pip
  deps = [
    pkgs.python312Full
    pkgs.python312Packages.pip
  ];
}
