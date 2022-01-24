from modules.init import folders
from modules.input import options
from modules.input import options_check
from modules.train import train

folders.make()
opt = options.parse_opt()
options_check.check_opt(opt)
