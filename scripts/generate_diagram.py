"""Generates docs/sequence-diagram.drawio for the AI agent request/response flow using drawpyo.

Run with: python3 scripts/generate_diagram.py
"""
import os

import drawpyo

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")

LIFELINE_TOP = 80
LIFELINE_BOTTOM = 650

# Lifeline x-centers
USER = 100
FRONTEND = 290
APIGW = 480
AGENT = 670
KB = 880


def add_participant(page, name, x):
    box = drawpyo.diagram.Object(page=page, value=name)
    box.position = (x - 70, 30)
    box.geometry.width = 140
    box.geometry.height = 40
    box.apply_style_string(
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;"
        "fontSize=12;fontStyle=1;align=center;verticalAlign=middle;"
    )
    return box


def add_lifeline(page, x):
    line = drawpyo.diagram.Object(page=page)
    line.position = (x - 1, LIFELINE_TOP)
    line.geometry.width = 2
    line.geometry.height = LIFELINE_BOTTOM - LIFELINE_TOP
    line.apply_style_string(
        "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#666666;dashed=1;"
    )
    return line


def add_activation(page, x, y_top, y_bottom):
    bar = drawpyo.diagram.Object(page=page)
    bar.position = (x - 5, y_top)
    bar.geometry.width = 10
    bar.geometry.height = y_bottom - y_top
    bar.apply_style_string(
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#333333;"
    )
    return bar


def add_anchor(page, x, y):
    anchor = drawpyo.diagram.Object(page=page)
    anchor.position = (x, y)
    anchor.geometry.width = 1
    anchor.geometry.height = 1
    anchor.apply_style_string("fillColor=none;strokeColor=none;")
    return anchor


def add_message(page, label, x1, y, x2, dashed=False):
    source = add_anchor(page, x1, y)
    target = add_anchor(page, x2, y)
    edge = drawpyo.diagram.Edge(page=page, source=source, target=target, label=label)
    edge.waypoints = "straight"
    edge.pattern = "dashed_medium" if dashed else "solid"
    edge.line_end_target = "block"
    edge.endFill_target = not dashed
    edge.line_end_source = None
    edge.strokeColor = "#333333"
    return edge


def add_fragment(page, label, x, y, width, height):
    frame = drawpyo.diagram.Object(page=page, value=label)
    frame.position = (x, y)
    frame.geometry.width = width
    frame.geometry.height = height
    frame.apply_style_string(
        "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#333333;"
        "verticalAlign=top;align=left;fontSize=11;fontStyle=1;spacingLeft=6;spacingTop=4;dashed=0;"
    )
    return frame


def add_note(page, text, x, y, width, height):
    note = drawpyo.diagram.Object(page=page, value=text)
    note.position = (x, y)
    note.geometry.width = width
    note.geometry.height = height
    note.apply_style_string(
        "shape=note;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;"
        "size=14;fontSize=10;align=left;verticalAlign=top;spacingLeft=4;spacingTop=4;"
    )
    return note


def add_marker(page, text, x, y, width):
    marker = drawpyo.diagram.Object(page=page, value=text)
    marker.position = (x, y)
    marker.geometry.width = width
    marker.geometry.height = 20
    marker.apply_style_string(
        "text;html=1;align=center;verticalAlign=middle;fontStyle=1;fontColor=#232F3E;fontSize=12;"
    )
    return marker


def build_diagram():
    file = drawpyo.File()
    file.file_name = "sequence-diagram.drawio"
    file.file_path = OUTPUT_DIR

    page = drawpyo.Page(file=file)
    page.name = "AI Agent Request Flow"

    add_marker(page, "\u25b6 START \u2014 user submits a question", 30, 5, 400)
    add_marker(page, "\u25a0 END \u2014 answer displayed to the user", 530, 660, 400)

    add_participant(page, "User", USER)
    add_participant(page, "Frontend\n(Web App)", FRONTEND)
    add_participant(page, "API Gateway", APIGW)
    add_participant(page, "AI Agent\n(Bedrock / Claude)", AGENT)
    add_participant(page, "Knowledge Base\n(RAG)", KB)

    for x in (USER, FRONTEND, APIGW, AGENT, KB):
        add_lifeline(page, x)

    add_activation(page, FRONTEND, 120, 600)
    add_activation(page, APIGW, 180, 560)
    add_activation(page, AGENT, 240, 500)
    add_activation(page, KB, 300, 370)

    # Request path
    add_message(page, "1: Ask question", USER, 120, FRONTEND)
    add_message(page, "2: POST /query {question}", FRONTEND, 180, APIGW)
    add_message(page, "3: Invoke agent (InvokeModel)", APIGW, 240, AGENT)

    add_fragment(
        page,
        "opt  [relevant context found in the knowledge base]",
        AGENT - 60,
        260,
        KB - AGENT + 120,
        130,
    )
    add_message(page, "4: Query knowledge base (RAG retrieval)", AGENT, 300, KB)
    add_message(page, "5: Return relevant context", KB, 370, AGENT, dashed=True)

    add_note(
        page,
        "Claude grounds its answer in the retrieved context when\n"
        "available, otherwise it falls back to the base model.",
        AGENT - 40,
        405,
        280,
        45,
    )

    # Response path
    add_message(page, "6: Return generated response", AGENT, 500, APIGW, dashed=True)
    add_message(page, "7: Return response", APIGW, 560, FRONTEND, dashed=True)
    add_message(page, "8: Display answer", FRONTEND, 600, USER, dashed=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file.write()
    print(f"Wrote {os.path.join(OUTPUT_DIR, file.file_name)}")


if __name__ == "__main__":
    build_diagram()
