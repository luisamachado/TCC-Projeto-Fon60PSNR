# TCC: Projeto FonPSNR

Projeto desenvolvido para codificar e analisar áudios de um diretório

Os áudios do diretório são codificados e decodificados usando os codecs Vorbis e Opus variando a taxa de bits (bitrate). Em seguida, cada áudio em seu formato original e decodificado passa pelas métricas do analisador e os resultados são registrados em uma planilha para análise posterior.

Este projeto também desenvolveu a nova métrica FonPSNR de avaliação objetiva da qualidade de áudio incorporando uma curva isofônica juntamente com relação sinal-ruído de pico PSNR.

## Execução do programa

Para execução deste projeto utilize o seguinte comando:

```python3 handle_change_params.py```