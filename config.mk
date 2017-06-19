[alias] k = log --graph --decorate --pretty=oneline --abbrev-commit lg = log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative [user]
      email = cleggm1@fnal.gov
      name = Melissa Clegg
[color]
      ui = auto
        diff = auto
        status = auto
        branch = auto
[push]
        default = matching
[pager]
        log = diff-highlight | less
        show = diff-highlight | less
        diff = diff-highlight | less
[interactive]
        diffFilter = diff-highlight
