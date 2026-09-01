#!/usr/bin/env python3
"""
Reaplica ajustes de enquadramento de foto que se perdem toda vez que o
index.html é substituído por uma nova exportação (o conteúdo novo vem
pronto do Drive e sobrescreve o arquivo inteiro, junto com qualquer
`object-position` ajustado manualmente antes).

Rodar depois de colar um index.html novo, antes de commitar.

Uso: python3 scripts/fix-known-crops.py [caminho/para/index.html]
"""
import re
import sys

# Cada entrada: um marcador de texto único que aparece perto da <img> a
# corrigir (ex.: o texto do <p class="eyebrow">), e o object-position a
# garantir nessa <img>. Adicionar novas entradas aqui conforme surgirem
# outras fotos com o mesmo problema recorrente.
FIXES = [
    {
        "nome": "seção 'O que a viagem não resolve' — foto corta a cabeça da Prema com foco central, rosto fica no lado direito da foto original",
        "marcador": "O que a viagem não resolve",
        "object_position": "82% center",
    },
]


def aplicar_fix(html: str, marcador: str, object_position: str, nome: str) -> str:
    pos = html.find(marcador)
    if pos == -1:
        print(f"[aviso] marcador não encontrado, pulando: {nome}")
        return html

    img_match = re.compile(r'<img\s+([^>]*?)src="([^"]*)"([^>]*)>').search(html, pos)
    if not img_match:
        print(f"[aviso] nenhuma <img> encontrada após o marcador, pulando: {nome}")
        return html

    full_tag = img_match.group(0)
    before, src, after = img_match.groups()
    attrs = before + after

    style_match = re.search(r'style="([^"]*)"', attrs)
    if style_match:
        style = style_match.group(1)
        if "object-position" in style:
            novo_style = re.sub(r'object-position:[^;]*', f'object-position:{object_position}', style)
        else:
            novo_style = f"{style};object-position:{object_position}"
        novos_attrs = attrs[:style_match.start()] + f'style="{novo_style}"' + attrs[style_match.end():]
    else:
        novos_attrs = attrs.rstrip() + f' style="object-position:{object_position}"'

    novo_tag = f'<img {novos_attrs.strip()} src="{src}">'
    # normaliza espaços duplicados
    novo_tag = re.sub(r'\s+', ' ', novo_tag).replace('<img ', '<img ', 1)

    if full_tag == novo_tag:
        print(f"[ok] já estava correto: {nome}")
        return html

    print(f"[fix] aplicado: {nome}")
    return html[:img_match.start()] + novo_tag + html[img_match.end():]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    for fix in FIXES:
        html = aplicar_fix(html, fix["marcador"], fix["object_position"], fix["nome"])

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
