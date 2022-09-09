
checkpoint_dict = {
    'resolution1024_bicubic': 'None',

    'resolution1024_swinir_lte': {
                                  '256x256': '/video-conf/scratch/pantea_experiments_mapmaker/super-resolution-weights/lte/swinir-lte.pth'
                                 },

    'resolution1024_occlusion_aware':{
        'needle_drop':{
                '64x64': { 'lrquantizer-1':{}},

                '128x128': { 'lrquantizer-1':{}},

                '256x256': { 'lrquantizer-1':{}},

                '512x512': {'lrquantizer-1':{}}
                      },

        'xiran': {
                '64x64': { 'lrquantizer-1': { 
                                            45: '/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/xiran1024_lr64_tgt45Kb 06_09_22_01.59.42/00000029-checkpoint.pth.tar'
                                            }
                         },

                '128x128': {
                            'lrquantizer-1':{
                                            15: '/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/xiran1024_lr128_tgt15Kb 05_09_22_02.28.19/00000029-checkpoint.pth.tar',
                                            45: '/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/xiran1024_lr128_tgt45Kb 06_09_22_01.59.09/00000029-checkpoint.pth.tar'
                                            }
                           },

                '256x256': {
                            'lrquantizer-1':{
                                            45:'/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/xiran1024_lr256_tgt45Kb 05_09_22_02.28.21/00000029-checkpoint.pth.tar',
                                            75: '/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/xiran1024_lr256_tgt75Kb 05_09_22_02.35.02/00000029-checkpoint.pth.tar',
                                            105: '/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/xiran1024_lr256_tgt105Kb 05_09_22_03.29.17/00000029-checkpoint.pth.tar'
                                            }
                           },

                '512x512':{}
                 },

        'kayleigh': { 
                '64x64': { 'lrquantizer-1':{
                                            45: '/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/kayleigh1024_lr64_tgt45Kb 06_09_22_22.13.09/00000029-checkpoint.pth.tar'
                                            }
                        },

                '128x128': { 'lrquantizer-1':{
                                            15: '/video-conf/scratch/vibhaa_lam2/encoder_fixed_bitrate/kayleigh1024_128lr_tgt15Kb 08_09_22_01.37.16/00000029-checkpoint.pth.tar',
                                            45: '/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/kayleigh1024_lr128_tgt45Kb 06_09_22_22.12.44/00000029-checkpoint.pth.tar'
                                             }
                           },

                '256x256': { 'lrquantizer-1':{
                                            45: '/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/xiran1024_lr256_tgt45Kb 05_09_22_02.28.21/00000029-checkpoint.pth.tar',
                                            75: '/video-conf/scratch/vibhaa_tardy/encoder_fixed_bitrate/kayleigh1024_lr256_tgt75Kb 06_09_22_22.15.44/00000029-checkpoint.pth.tar',
                                            105: '/video-conf/scratch/vibhaa_lam2/encoder_fixed_bitrate/kayleigh1024_256lr_tgt105Kb 07_09_22_05.04.40/00000029-checkpoint.pth.tar'
                                             }
                           },

                '512x512': {'lrquantizer-1':{}}
                    },

        'adam_neely': {
                '64x64': {'lrquantizer-1':{
                                            45: '/video-conf/scratch/vibhaa_lam1/encoder_fixed_bitrate/adam_neely1024_64lr_tgt45Kb 07_09_22_13.21.45/00000029-checkpoint.pth.tar'
                                          }
                         },

                '128x128': {'lrquantizer-1':{
                                            15: '/video-conf/scratch/vibhaa_lam1/encoder_fixed_bitrate/adam_neely1024_128lr_tgt15Kb 07_09_22_13.20.24/00000029-checkpoint.pth.tar',
                                            45: '/video-conf/scratch/vibhaa_lam1/encoder_fixed_bitrate/adam_neely1024_128lr_tgt45Kb 07_09_22_13.21.19/00000029-checkpoint.pth.tar'
                                            }
                           },

                '256x256': {'lrquantizer-1':{
                                            45: '/video-conf/scratch/vibhaa_lam1/encoder_fixed_bitrate/adam_neely1024_256lr_tgt45Kb 07_09_22_13.19.39/00000029-checkpoint.pth.tar',
                                            75: '/video-conf/scratch/vibhaa_lam1/encoder_fixed_bitrate/adam_neely1024_256lr_tgt75Kb 07_09_22_13.19.06/00000029-checkpoint.pth.tar',
                                            105: '/video-conf/scratch/vibhaa_lam1/encoder_fixed_bitrate/adam_neely1024_256lr_tgt105Kb 07_09_22_13.18.03/00000029-checkpoint.pth.tar'
                                            }
                           },

                '512x512': {'lrquantizer-1':{}}
                      },

        'fancy_fueko': {
                '64x64': { 'lrquantizer-1':{}},

                '128x128': { 'lrquantizer-1':{}},

                '256x256': { 'lrquantizer-1':{}},

                '512x512': {'lrquantizer-1':{}}
                        }
    },

    'resolution1024_occlusion_aware_no_encoder': {
            'needle_drop': {},
            'xiran': '/video-conf/scratch/vibhaa_lam2/model_arch_comparison/xiran1024_fomm_3_pathways_with_occlusion 07_09_22_05.03.13/00000029-checkpoint.pth.tar',
            'fancy_fueko': {},
            'adam_neely': {},
            'kayleigh': {}

    }
}
