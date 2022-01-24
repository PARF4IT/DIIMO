import torch


def check_opt(args):
    passer = []
    worker = str(args.worker)

    if worker.lower() == 'gpu':
        if torch.cuda.is_available():
            worker = "cuda"
            print(f"{worker}를 사용합니다.")
        else:
            worker = "cpu"
            print(f"gpu사용이 불가합니다. gpu대신 {worker}를 사용합니다.")

    else:
        worker = "cpu"
        print(f"{worker}를 사용합니다.")

    passer.append(worker)

    return passer
