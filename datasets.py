import numpy as np
import torchvision
from torch.utils.data import Dataset
from torchvision.datasets import SVHN, MNIST, USPS
from pacs import PACS
from PIL import Image
import pdb
from torchvision import transforms
from PIL import ImageFilter
import random
from mnistm import MNISTM
from visdac import VISDAC
from domainnet import DomainNet

class GaussianBlur(object):
    """Gaussian blur augmentation in SimCLR https://arxiv.org/abs/2002.05709"""

    def __init__(self, sigma=[0.1, 2.0]):
        self.sigma = sigma

    def __call__(self, x):
        sigma = random.uniform(self.sigma[0], self.sigma[1])
        x = x.filter(ImageFilter.GaussianBlur(radius=sigma))
        return x

normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        )

strong_augmentation = transforms.Compose(
            [
                transforms.RandomResizedCrop(28, scale=(0.2, 1.0)),
                transforms.RandomApply(
                    [transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)],
                    p=0.8,  # not strengthened
                ),
                transforms.RandomGrayscale(p=0.2),
                transforms.RandomApply([GaussianBlur([0.1, 2.0])], p=0.5),
                transforms.RandomHorizontalFlip(),
                transforms.Resize(32),
                transforms.ToTensor(),
                normalize,
            ]
        )

base_aug = transform=transforms.Compose([transforms.Resize((32,32)), transforms.ToTensor(), transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))])

class dataset(Dataset):
    def __init__(self, dataset, root, mode, transform, noisy_path=None):
        self.dataset = dataset
        self.root = root
        self.mode = mode
        self.transform = transform
        self.noisy_path = noisy_path
    
        self.parse_dataset()

    def parse_dataset(self):
        if self.dataset == 'mnist':
            return self.get_mnist()
        elif self.dataset == 'mnistm':
            return self.get_mnistm()
        elif self.dataset == 'svhn':
            return self.get_svhn()
        elif self.dataset == 'usps':
            return self.get_usps()
        elif self.dataset.split('/')[0] == 'pacs':
            return self.get_pacs()
        elif self.dataset.split('/')[0] == 'visdac':
            return self.get_visdac()
        elif self.dataset.split('/')[0] == 'domainnet':
            return self.get_domainnet()

    def get_svhn(self):
        if self.mode == 'all':
            train_set = SVHN(root=self.root,
                                    download=True,
                                    split='train',
                                    transform=self.transform
                                    )
            
            test_set = SVHN(root=self.root,
                                    download=True,
                                    split='test',
                                    transform=self.transform
                                    )
            
            data = np.concatenate((train_set.data, test_set.data))
            labels = np.concatenate((train_set.labels, test_set.labels))

        else:
            dataset = SVHN(root=self.root,
                                    download=True,
                                    split=self.mode,
                                    transform=self.transform
                                    )
            data = dataset.data
            labels = dataset.labels

        data = np.transpose(data, (0,2,3,1))

        self.strong_augmentation = transforms.Compose(
            [
                transforms.RandomResizedCrop(28, scale=(0.2, 1.0)),
                transforms.RandomApply(
                    [transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)],
                    p=0.8,  # not strengthened
                ),
                transforms.RandomGrayscale(p=0.2),
                transforms.RandomApply([GaussianBlur([0.1, 2.0])], p=0.5),
                transforms.RandomHorizontalFlip(),
                transforms.Resize(32),
                transforms.ToTensor(),
                normalize,
            ]
        )
        
        if self.noisy_path is not None:
            idx, noisy_labels = self.load_noisy_labels()

            self.data = data[idx]
            self.labels = labels[idx]
            self.noisy_labels = noisy_labels
        else:
            self.data = data
            self.labels = labels

    def get_mnist(self):
        if self.mode == 'all':
            train_set = MNIST(root=self.root,
                                    download=True,
                                    train=True,
                                    transform=self.transform
                                    )
            
            test_set = MNIST(root=self.root,
                                    download=True,
                                    train=False,
                                    transform=self.transform
                                    )
            
            data = np.concatenate((train_set.data, test_set.data))
            labels = np.concatenate((train_set.targets, test_set.targets))

        else:
            train = True if self.mode == 'train' else False
            dataset = MNIST(root=self.root,
                                    download=True,
                                    train=train,
                                    transform=self.transform
                                    )
            data = dataset.data
            labels = dataset.targets
        
        self.strong_augmentation = transforms.Compose(
            [
                transforms.RandomResizedCrop(28, scale=(0.2, 1.0)),
                transforms.RandomApply(
                    [transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)],
                    p=0.8,  # not strengthened
                ),
                transforms.RandomGrayscale(p=0.2),
                transforms.RandomApply([GaussianBlur([0.1, 2.0])], p=0.5),
                transforms.RandomHorizontalFlip(),
                transforms.Resize(32),
                transforms.ToTensor(),
                normalize,
            ]
        )

        if self.noisy_path is not None:
            idx, noisy_labels = self.load_noisy_labels()

            self.data = data[idx]
            self.labels = labels[idx]
            self.noisy_labels = noisy_labels
        else:
            self.data = data
            self.labels = labels
    
    def get_mnistm(self):
        if self.mode == 'all':
            train_set = MNISTM(root=self.root,
                                    download=True,
                                    train=True,
                                    transform=self.transform
                                    )
            
            test_set = MNISTM(root=self.root,
                                    download=True,
                                    train=False,
                                    transform=self.transform
                                    )
            
            data = np.concatenate((train_set.data, test_set.data))
            labels = np.concatenate((train_set.targets, test_set.targets))

        else:
            train = True if self.mode == 'train' else False
            dataset = MNISTM(root=self.root,
                                    download=True,
                                    train=train,
                                    transform=self.transform
                                    )
            data = dataset.data
            labels = dataset.targets

        self.strong_augmentation = transforms.Compose(
            [
                transforms.RandomResizedCrop(28, scale=(0.2, 1.0)),
                transforms.RandomApply(
                    [transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)],
                    p=0.8,  # not strengthened
                ),
                transforms.RandomGrayscale(p=0.2),
                transforms.RandomApply([GaussianBlur([0.1, 2.0])], p=0.5),
                transforms.RandomHorizontalFlip(),
                transforms.Resize(32),
                transforms.ToTensor(),
                normalize,
            ]
        )

        if self.noisy_path is not None:
            idx, noisy_labels = self.load_noisy_labels()

            self.data = data[idx]
            self.labels = labels[idx]
            self.noisy_labels = noisy_labels
        else:
            self.data = data
            self.labels = labels

    def get_usps(self):
        if self.mode == 'all':
            train_set = USPS(root=self.root,
                                    train=True,
                                    transform=self.transform
                                    )
            
            test_set = USPS(root=self.root,
                                    download=True,
                                    train=False,
                                    transform=self.transform
                                    )
            
            data = np.concatenate((train_set.data, test_set.data))
            labels = np.concatenate((train_set.targets, test_set.targets))

        else:
            train = True if self.mode == 'train' else False
            dataset = USPS(root=self.root,
                                    download=True,
                                    train=train,
                                    transform=self.transform
                                    )
            data = dataset.data
            labels = dataset.targets

        self.strong_augmentation = transforms.Compose(
            [
                transforms.RandomResizedCrop(28, scale=(0.2, 1.0)),
                transforms.RandomApply(
                    [transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)],
                    p=0.8,  # not strengthened
                ),
                transforms.RandomGrayscale(p=0.2),
                transforms.RandomApply([GaussianBlur([0.1, 2.0])], p=0.5),
                transforms.RandomHorizontalFlip(),
                transforms.Resize(32),
                transforms.ToTensor(),
                normalize,
            ]
        )

        if self.noisy_path is not None:
            idx, noisy_labels = self.load_noisy_labels()

            self.data = data[idx]
            self.labels = labels[idx]
            self.noisy_labels = noisy_labels
        else:
            self.data = data
            self.labels = labels

    def get_pacs(self):
        domain = self.dataset.split('/')[-1]

        if self.mode == 'all':
            train_set = PACS(root=self.root,
                                    domain=domain,
                                    train=True,
                                    transform=self.transform,
                                    from_file=True
                                    )
            
            test_set = PACS(root=self.root,
                                    domain=domain,
                                    train=False,
                                    transform=self.transform,
                                    from_file=True
                                    )
            
            data = np.concatenate((train_set.data, test_set.data))
            labels = np.concatenate((train_set.labels, test_set.labels))

        else:
            train = True if self.mode == 'train' else False
            dataset = PACS(root=self.root,
                                    domain=domain,
                                    train=train,
                                    transform=self.transform,
                                    from_file=True
                                    )
            data = dataset.data
            labels = dataset.labels

        self.strong_augmentation = transforms.Compose(
            [
                transforms.RandomResizedCrop(224, scale=(0.2, 1.0)),
                transforms.RandomApply(
                    [transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)],
                    p=0.8,  # not strengthened
                ),
                transforms.RandomGrayscale(p=0.2),
                transforms.RandomApply([GaussianBlur([0.1, 2.0])], p=0.5),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                normalize,
            ]
        )

        if self.noisy_path is not None:
            idx, noisy_labels = self.load_noisy_labels()

            self.data = data[idx]
            self.labels = labels[idx]
            self.noisy_labels = noisy_labels
        else:
            self.data = data
            self.labels = labels

    def get_visdac(self):
        domain = self.dataset.split('/')[-1]

        if self.mode == 'all':
            train_set = VISDAC(root=self.root,
                                    domain=domain,
                                    train=True,
                                    transform=self.transform,
                                    from_file=True
                                    )
            
            test_set = VISDAC(root=self.root,
                                    domain=domain,
                                    train=False,
                                    transform=self.transform,
                                    from_file=True
                                    )
            
            data = np.concatenate((train_set.data, test_set.data))
            labels = np.concatenate((train_set.labels, test_set.labels))

        else:
            train = True if self.mode == 'train' else False
            dataset = VISDAC(root=self.root,
                                    domain=domain,
                                    train=train,
                                    transform=self.transform,
                                    from_file=True
                                    )
            data = dataset.data
            labels = dataset.labels

        self.strong_augmentation = transforms.Compose(
            [
                transforms.RandomResizedCrop(224, scale=(0.2, 1.0)),
                transforms.RandomApply(
                    [transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)],
                    p=0.8,  # not strengthened
                ),
                transforms.RandomGrayscale(p=0.2),
                transforms.RandomApply([GaussianBlur([0.1, 2.0])], p=0.5),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                normalize,
            ]
        )

        self.data = data
        self.labels = labels

    def get_domainnet(self):
        domain = self.dataset.split('/')[-1]

        if self.mode == 'all':
            train_set = DomainNet(root=self.root,
                                    domain=domain,
                                    train=True,
                                    transform=self.transform,
                                    from_file=True
                                    )
            
            test_set = DomainNet(root=self.root,
                                    domain=domain,
                                    train=False,
                                    transform=self.transform,
                                    from_file=True
                                    )
            
            data = np.concatenate((train_set.data, test_set.data))
            labels = np.concatenate((train_set.labels, test_set.labels))

        else:
            train = True if self.mode == 'train' else False
            dataset = DomainNet(root=self.root,
                                    domain=domain,
                                    train=train,
                                    transform=self.transform,
                                    from_file=True
                                    )
            data = dataset.data
            labels = dataset.labels

        self.strong_augmentation = transforms.Compose(
            [
                transforms.RandomResizedCrop(224, scale=(0.2, 1.0)),
                transforms.RandomApply(
                    [transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)],
                    p=0.8,  # not strengthened
                ),
                transforms.RandomGrayscale(p=0.2),
                transforms.RandomApply([GaussianBlur([0.1, 2.0])], p=0.5),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                normalize,
            ]
        )

        self.data = data
        self.labels = labels


    def load_noisy_labels(self):
        idx = np.load(self.noisy_path+"_idx.npy")
        labels = np.load(self.noisy_path+"_noisylab.npy")

        return idx, labels

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (image, target) where target is index of the target class.
        """

        img, target = self.data[index], self.labels[index]
        noisy_target = self.noisy_labels[index] if self.noisy_path is not None else self.labels[index]

        if self.dataset in ['mnist', 'mnistm'] and self.mode != 'all':
            img = Image.fromarray(img.numpy())
        elif self.dataset.split('/')[0] in ['pacs', 'visdac', 'domainnet']:
            img = Image.fromarray(img)
        else:
            img = Image.open(img)

        if self.dataset in ['mnist', 'usps']:
            img = transforms.Grayscale(3)(img)

        strong_augmented = self.strong_augmentation(img)
        strong_augmented2 = self.strong_augmentation(img)
        weak_augmented = self.transform(img) if self.transform is not None else img

        return weak_augmented, strong_augmented, target, index, noisy_target, strong_augmented2#, img

    def __len__(self) -> int:
        return len(self.data)