// Micro theme for Pegasus
// Copyright (C) 2019  Mátyás Mustoha

import QtQuick 2.2
import QtQuick.Window 2.2

Item {
    id: root

    property var game

    property alias imageWidth: img.paintedWidth
    property alias imageHeight: img.paintedHeight

    signal clicked()
    signal doubleClicked()
    signal imageLoaded(int imgWidth, int imgHeight)

    Behavior on scale { PropertyAnimation { duration: 150 } }

    Image {
        id: img
        anchors.fill: parent
        anchors.margins: parent.width * 0.025
        fillMode: Image.PreserveAspectFit

        source: game.assets.boxFront
            || game.assets.poster
            || game.assets.banner
            || game.assets.steam
            || game.assets.tile
            || game.assets.cartridge
        sourceSize { width: 500; height: 500 }
        asynchronous: true

        opacity: 0
        Behavior on opacity { NumberAnimation { duration: 100 } }

        onStatusChanged: if (status === Image.Ready) {
            opacity = 1.0;
            root.imageLoaded(paintedWidth, paintedHeight);
        }
        Component.onCompleted: if (status === Image.Ready) {
            opacity = 1.0;
            root.imageLoaded(paintedWidth, paintedHeight);
        }
    }

    Text {
        anchors.fill: parent
        anchors.margins: parent.width * 0.1
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter

        visible: img.status != Image.Ready && img.status != Image.Loading

        text: game.title
        wrapMode: Text.Wrap
        elide: Text.ElideRight
        color: "#eee"
        font.pixelSize: Window.window.height * 0.06
        font.family: global.fonts.sans
    }

    MouseArea {
        anchors.fill: parent
        onClicked: root.clicked()
        onDoubleClicked: root.doubleClicked()
    }
}
