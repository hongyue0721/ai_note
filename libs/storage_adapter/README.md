# Storage Adapter

用于封装对象存储抽象。

首轮仅建立目录，后续实现：

- `StorageProvider` 抽象
- `MinioStorageProvider`
- `QiniuStorageProvider`
- 上传策略生成
- 文件确认与元数据回写
