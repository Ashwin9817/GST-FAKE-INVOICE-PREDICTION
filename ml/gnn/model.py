"""
GraphSAGE Neural Network Architecture.
Learns 64-dimensional node vector representations via multi-hop message passing.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class GraphSAGEConv(nn.Module):
    """Custom PyTorch GraphSAGE Message Passing Layer (Mean Aggregation)."""

    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.lin_self = nn.Linear(in_features, out_features, bias=True)
        self.lin_neigh = nn.Linear(in_features, out_features, bias=False)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Forward message passing pass.
        x: [num_nodes, in_features]
        edge_index: [2, num_edges]
        """
        num_nodes = x.size(0)
        src, dst = edge_index[0], edge_index[1]

        # Compute mean neighbor aggregation
        neigh_sum = torch.zeros(num_nodes, x.size(1), device=x.device)
        neigh_count = torch.zeros(num_nodes, 1, device=x.device)

        neigh_sum.index_add_(0, dst, x[src])
        ones = torch.ones(src.size(0), 1, device=x.device)
        neigh_count.index_add_(0, dst, ones)

        neigh_mean = neigh_sum / torch.clamp(neigh_count, min=1.0)

        out = self.lin_self(x) + self.lin_neigh(neigh_mean)
        return out

class GraphSAGENet(nn.Module):
    """2-Layer GraphSAGE Architecture for GST Business Graph Embedding Learning."""

    def __init__(self, in_channels: int, hidden_channels: int = 128, out_channels: int = 64, dropout: float = 0.2):
        super().__init__()
        self.conv1 = GraphSAGEConv(in_channels, hidden_channels)
        self.conv2 = GraphSAGEConv(hidden_channels, out_channels)
        self.dropout = dropout

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        x: Node feature tensor [num_nodes, in_channels]
        edge_index: Graph adjacency edge index tensor [2, num_edges]
        Returns: Learned node embeddings tensor [num_nodes, out_channels]
        """
        h = self.conv1(x, edge_index)
        h = F.relu(h)
        h = F.dropout(h, p=self.dropout, training=self.training)

        embeddings = self.conv2(h, edge_index)
        return embeddings
