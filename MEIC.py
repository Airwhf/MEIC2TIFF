#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2023/4/26 18:52
# @Author    :Haofan Wang
# @Email     :wanghf58@mail2.sysu.edu.cn
import glob
import os.path

import tqdm
import xarray as xr
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS
import re

if __name__ == "__main__":
    print("This script is written by Haofan Wang.")
    # ------------------------------------------
    input_dir = r"E:\MEIC\MEIC_SPARC07_2017"
    output_dir = r"E:\MEIC\MEIC_SPARC07_2017"
    # ------------------------------------------

    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)

    files = glob.glob(f"{input_dir}/*.nc")
    for file in tqdm.tqdm(files):
        sub_name = os.path.basename(file)
        condition = f"(.*?)_(.*?)_(.*?)_(.*?).nc"
        encode_name = re.findall(condition, sub_name)[0]
        year = r"%.4d" % int(encode_name[0])
        mm = r"%.2d" % int(encode_name[1])
        sector = encode_name[2]
        pollutant = encode_name[3]
        output_name = f"{output_dir}/MEIC_{year}_{mm}__{sector}__{pollutant}.tiff"

        ds = xr.open_dataset(file)
        _ = np.reshape(ds["z"].values, (ds["dimension"].values[1], ds["dimension"].values[0]))
        # Convert -9999.0 to 0.0.
        z = np.where(_ == -9999.0, 0.0, _)

        # 最大最小经纬度
        min_long, min_lat, max_long, max_lat = ds["x_range"].values[0], ds["y_range"].values[0], ds["x_range"].values[1], ds["y_range"].values[1]

        # 分辨率
        x_resolution = ds["spacing"].values[0]
        y_resolution = ds["spacing"].values[1]

        # 计算栅格的行和列
        width = int((max_long - min_long) / x_resolution)
        height = int((max_lat - min_lat) / y_resolution)

        # 创建GeoTIFF文件的变换矩阵
        transform = from_bounds(min_long, min_lat, max_long, max_lat, width, height)

        # 定义GeoTIFF文件的元数据
        metadata = {
            "driver": "GTiff",
            "height": height,
            "width": width,
            "count": 1,
            "dtype": rasterio.float32,
            "crs": CRS.from_epsg(4326),
            "transform": transform,
        }

        # 创建GeoTIFF文件
        with rasterio.open(output_name, "w", **metadata) as dst:
            dst.write(z, 1)  # 将数据写入波段1
