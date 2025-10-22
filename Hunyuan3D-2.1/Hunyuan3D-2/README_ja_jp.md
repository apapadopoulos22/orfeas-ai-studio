[Read in English](README.md)
[](README_zh_cn.md)

<p align="center">
  <img src="./assets/images/teaser.jpg">

</p>

<div align="center">
  <a href=https://3d.hunyuan.tencent.com target="_blank"><img src=https://img.shields.io/badge/Official%20Site-black.svg?logo=homepage height=22px></a>
  <a href=https://huggingface.co/spaces/tencent/Hunyuan3D-2  target="_blank"><img src=https://img.shields.io/badge/%F0%9F%A4%97%20Demo-276cb4.svg height=22px></a>
  <a href=https://huggingface.co/tencent/Hunyuan3D-2 target="_blank"><img src=https://img.shields.io/badge/%F0%9F%A4%97%20Models-d96902.svg height=22px></a>
  <a href=https://3d-models.hunyuan.tencent.com/ target="_blank"><img src= https://img.shields.io/badge/Page-bb8a2e.svg?logo=github height=22px></a>
  <a href=https://discord.gg/dNBrdrGGMa target="_blank"><img src= https://img.shields.io/badge/Discord-white.svg?logo=discord height=22px></a>
  <a href=https://github.com/Tencent/Hunyuan3D-2/blob/main/assets/report/Tencent_Hunyuan3D_2_0.pdf target="_blank"><img src=https://img.shields.io/badge/Report-b5212f.svg?logo=arxiv height=22px></a>
</div>

[//]: # (  <a href=# target="_blank"><img src=https://img.shields.io/badge/Report-b5212f.svg?logo=arxiv height=22px></a>)

[//]: # (  <a href=# target="_blank"><img src= https://img.shields.io/badge/Colab-8f2628.svg?logo=googlecolab height=22px></a>)

[//]: # (  <a href="#"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/v/mulankit?logo=pypi"  height=22px></a>)

<br>
<p align="center">
" 3D"
</p>

##

- 2025214:  HD  [](minimal_demo.py)
- 2025121:   [Hunyuan3D Studio](https://3d.hunyuan.tencent.com) 3D!
- 2025121:  [Hunyuan3D 2.0](https://huggingface.co/tencent/Hunyuan3D-2)
- 2025121:  Hunyuan3D 2.0 [huggingface space](https://huggingface.co/spaces/tencent/Hunyuan3D-2)  [](https://3d.hunyuan.tencent.com) !

## ****

Hunyuan3D 2.03D3D
2: - Hunyuan3D-DiT

 - Hunyuan3D-Paint

Hunyuan3D-Studio3D

Hunyuan3D 2.0

<p align="center">
  <img src="assets/images/system.jpg">
</p>

##  Hunyuan3D 2.0

###

Hunyuan3D 2.02

<p align="left">
  <img src="assets/images/arch.jpg">
</p>

###

Hunyuan3D 2.03D
Hunyuan3D 2.03D

|                    | CMMD()   | FID_CLIP() | FID()      | CLIP-score() |
|-------------------------|-----------|-------------|-------------|---------------|
| 1  | 3.591     | 54.639      | 289.287     | 0.787         |
| 1 | 3.600     | 55.866      | 305.922     | 0.779         |
| 2 | 3.368     | 49.744      | 294.628     | 0.806         |
| 3 | 3.218     | 51.574      | 295.691     | 0.799         |
| Hunyuan3D 2.0           | **3.193** | **49.165**  | **282.429** | **0.809**     |

Hunyuan3D 2.0:
<p align="left">
  <img src="assets/images/e2e-1.gif"  height=250>
  <img src="assets/images/e2e-2.gif"  height=250>
</p>

###

|                 |        | Huggingface                                            |
|----------------------|------------|--------------------------------------------------------|
| Hunyuan3D-DiT-v2-0   | 2025-01-21 | [](https://huggingface.co/tencent/Hunyuan3D-2) |
| Hunyuan3D-Paint-v2-0 | 2025-01-21 | [](https://huggingface.co/tencent/Hunyuan3D-2) |

##  Hunyuan3D 2.0

GradioHunyuan3D 2.0

###

Pytorch

```bash
pip install -r requirements.txt

# for texture

cd hy3dgen/texgen/custom_rasterizer
python3 setup.py install
cd hy3dgen/texgen/differentiable_renderer
python3 setup.py install

```text

## API

 - Hunyuan3D-DiT - Hunyuan3D-PaintdiffusersAPI

**Hunyuan3D-DiT**:

```python
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('tencent/Hunyuan3D-2')
mesh = pipeline(image='assets/demo.png')[0]

```text

[trimesh](https://trimesh.org/trimesh.html)glb/obj()

**Hunyuan3D-Paint**:

```python
from hy3dgen.texgen import Hunyuan3DPaintPipeline
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

#

pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('tencent/Hunyuan3D-2')
mesh = pipeline(image='assets/demo.png')[0]

pipeline = Hunyuan3DPaintPipeline.from_pretrained('tencent/Hunyuan3D-2')
mesh = pipeline(mesh, image='assets/demo.png')

```text

[minimal_demo.py](minimal_demo.py)**3D******

### Gradio

[Gradio](https://www.gradio.app/):

```bash
python3 gradio_app.py

```text

[Hunyuan3D](https://3d.hunyuan.tencent.com)

##

- [x]
- [x]
- [x]
- [ ] ComfyUI
- [ ] TensorRT

##  BibTeX

:

```bibtex
@misc{hunyuan3d22025tencent,
    title={Hunyuan3D 2.0: Scaling Diffusion Models for High Resolution Textured 3D Assets Generation},
    author={Tencent Hunyuan3D Team},
    year={2025},
    eprint={2501.12202},
    archivePrefix={arXiv},
    primaryClass={cs.CV}
}

@misc{yang2024hunyuan3d,
    title={Hunyuan3D 1.0: A Unified Framework for Text-to-3D and Image-to-3D Generation},
    author={Tencent Hunyuan3D Team},
    year={2024},
    eprint={2411.02293},
    archivePrefix={arXiv},
    primaryClass={cs.CV}
}

```text

##

[DINOv2](https://github.com/facebookresearch/dinov2), [Stable Diffusion](https://github.com/Stability-AI/stablediffusion), [FLUX](https://github.com/black-forest-labs/flux), [diffusers](https://github.com/huggingface/diffusers), [HuggingFace](https://huggingface.co), [CraftsMan3D](https://github.com/wyysf-98/CraftsMan3D), and [Michelangelo](https://github.com/NeuralCarver/Michelangelo/tree/main)

##

<a href="https://star-history.com/#Tencent/Hunyuan3D-2&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Tencent/Hunyuan3D-2&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Tencent/Hunyuan3D-2&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Tencent/Hunyuan3D-2&type=Date" />
 </picture>
</a>
