
checkpoint_dict = {
    'resolution1024_bicubic': 'None',

    'resolution1024_swinir_lte': {
                                  '256x256': '/video-conf/scratch/pantea_experiments_mapmaker/super-resolution-weights/lte/swinir-lte.pth'
                                 },

    'resolution1024_occlusion_aware':{
        'needle_drop':{},

        'xiran': {
                '64x64': {},

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

        'kayleigh': {},

        'adam_neely': {},

        'fancy_fueko': {}
    }
}
