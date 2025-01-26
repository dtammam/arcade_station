import QtQuick 2.0

PathView {
    id: root

    pathItemCount: 3
    path: Path {
        startX: -root.width
        startY: root.height / 2
        PathLine {
            x: root.width * 2
            y: root.path.startY
        }
    }

    snapMode: PathView.SnapOneItem
    preferredHighlightBegin: 0.5
    preferredHighlightEnd: 0.5

    delegate: Item {
        width: root.width * 0.85
        height: root.height * 0.66

        Image {
            id: img
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit

            source: "assets/logos/" + shortName + ".png"
            sourceSize { width: 128; height: 128 }
            asynchronous: true
        }
        Text {
            text: modelData.name
            anchors.fill: parent
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.bold: true
            font.capitalization: Font.AllUppercase
            font.pixelSize: parent.height * 0.85
            font.family: global.fonts.condensed
            color: "#fff"
            elide: Text.ElideRight
            visible: img.status !== Image.Ready && img.status !== Image.Loading
        }
    }


    Rectangle {
        anchors.fill: parent
        color: "#000"
        z: -1
    }
}
