import QtQuick 2.0

GridView {
    id: grid

    signal gameOpened()
							//the number at the end of this line is how many columns of games
    readonly property int columnCount: cellHeightRatio > 0.85 ? 3 : 3

    property bool firstImageLoaded: false
    property real cellHeightRatio: 0.5

    function cells_need_recalc() {
        firstImageLoaded = false;
        cellHeightRatio = 0.5;
    }

    function calc_height_ratio(imageW, imageH) {
        if (imageW > 0 && imageH > 0)
            cellHeightRatio = imageH / imageW;
    }

    // make sure cells are reset *before* changing to a new model
    property var realModel
    onRealModelChanged: { cells_need_recalc(); model = realModel; }

    cellWidth: width / columnCount
    cellHeight: cellWidth * cellHeightRatio

    highlightMoveDuration: 100
    highlight: Rectangle {
        color: "#0074da"
        width: cellWidth
        height: cellHeight
    }

    delegate: GameGridItem {
        width: cellWidth
        height: cellHeight
        game: modelData

        onClicked: grid.currentIndex = index
        onDoubleClicked: game.launch()
        Keys.onPressed: {
            if (event.isAutoRepeat)
                return;
            if (api.keys.isAccept(event)) {
                event.accepted = true;
                game.launch()
            }
        }

        onImageLoaded: {
            if (!grid.firstImageLoaded) {
                grid.firstImageLoaded = true;
                grid.calc_height_ratio(imgWidth, imgHeight);
            }
        }
    }
}
