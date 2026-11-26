# Third-party notices

## Pretrained models

| Model file | Upstream source | License metadata |
| --- | --- | --- |
| `models/style_transfer/inceptionv3-predict_int8.tflite` | [Arbitrary Image Stylization — prediction](https://www.kaggle.com/models/spsayakpaul/arbitrary-image-stylization-inceptionv3) | Apache-2.0 |
| `models/style_transfer/inceptionv3-transfer_int8.tflite` | [Arbitrary Image Stylization — transformation](https://www.kaggle.com/models/spsayakpaul/arbitrary-image-stylization-inceptionv3) | Apache-2.0 |
| `models/cartoongan_dr.tflite` | [CartoonGAN](https://www.kaggle.com/models/spsayakpaul/cartoongan) | Apache-2.0 |

Model publisher: Sayak Paul. See the [stylization model card](https://github.com/tensorflow/tfhub.dev/blob/master/assets/docs/sayakpaul/arbitrary-image-stylization-inceptionv3/1.md) and [cartoon model card](https://github.com/tensorflow/tfhub.dev/blob/master/assets/docs/sayakpaul/cartoongan/1.md). A copy of the [Apache 2.0 license](licenses/Apache-2.0.txt) is included. Exact upstream binary identity and additional notice obligations have not been verified.

Research references:

- Ghiasi et al., [Exploring the Structure of a Real-Time, Arbitrary Neural Artistic Stylization Network](https://arxiv.org/abs/1705.06830), 2017.
- Wang and Yu, Learning to Cartoonize Using White-Box Cartoon Representations, 2020.

## Image assets

The style reference files and corresponding thumbnails in `models/style_transfer/images/` and `static/images/style-template/` include artwork attributed in their filenames. Historical artwork may be in the public domain, but the rights to the specific reproductions and other references have not been established. The source and redistribution rights of the interface illustrations, logo, and `modules/pencil_sketch/shading-background.jpg` also remain unverified. These assets are retained from the original application; their inclusion does not grant redistribution permission. Verify rights before public distribution or replace assets lacking permission.

## Interface resources

Bootstrap 5.3.3 and the Poppins font are loaded from external CDNs. Consult their upstream licenses for applicable terms.
