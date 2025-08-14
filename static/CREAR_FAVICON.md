# Cómo crear el archivo w.ico

## Opción 1: Usar herramienta online
1. Ve a https://favicon.io/favicon-converter/
2. Sube el archivo `w.svg` que está en esta carpeta
3. Descarga el `favicon.ico` generado
4. Renómbralo a `w.ico` y colócalo en esta carpeta

## Opción 2: Usar ImageMagick (si lo tienes instalado)
```bash
convert w.svg -resize 32x32 w.ico
```

## Opción 3: Usar GIMP
1. Abre `w.svg` en GIMP
2. Exporta como `w.ico`
3. Selecciona tamaños: 16x16, 32x32, 48x48

## Nota
Mientras tanto, el navegador usará el archivo `w.svg` como favicon, que funciona perfectamente en navegadores modernos.

El archivo `w.svg` ya está creado con:
- Gradiente azul-púrpura (igual que el diseño)
- Letra "W" blanca centrada
- Tamaño 32x32 píxeles
- Esquinas redondeadas