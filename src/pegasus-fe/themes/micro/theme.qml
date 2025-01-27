import QtQuick 2.0

FocusScope {
    id: root

    Keys.onPressed: {
        if (event.isAutoRepeat)
            return;

        if (api.keys.isPrevPage(event)) {
            event.accepted = true;
            return topbar.decrementCurrentIndex();
        }
        if (api.keys.isNextPage(event)) {
            event.accepted = true;
            return topbar.incrementCurrentIndex();
        }
    }

    CollectionBar {
        id: topbar

        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: parent.height * 0.12

        model: api.collections
        readonly property var current: api.collections.get(currentIndex)

        z: 2
    }

    GameGrid {
        id: grid

        anchors.fill: parent
        anchors.topMargin: topbar.height + cellHeight * 0.025
        focus: true

        realModel: topbar.current.games
        onGameOpened: gamepage.focus = true
        readonly property var current: realModel.get(currentIndex)
    }

    GamePage {
        id: gamepage
        anchors.fill: parent
        visible: opacity > 0.01
        opacity: focus ? 1.0 : 0.0
        z: 3

        readonly property var game: grid.current
        onClose: grid.focus = true

        Behavior on opacity { NumberAnimation { duration: 150 } }
    }
}
