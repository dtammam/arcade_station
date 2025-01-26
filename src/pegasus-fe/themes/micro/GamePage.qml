import QtQuick 2.6
import QtMultimedia 5.6
import "qrc:/qmlutils" as PegasusUtils


Rectangle {
    id: root
    color: "#333"

    signal close()

    onFocusChanged: {
        if (focus) {
            leftbarList.currentIndex = 0; // select Description
            bottombar.currentIndex = bottombar.model.length - 1; // select Launch
        }
    }

    Keys.forwardTo: [leftbarList, bottombar]
    Keys.onPressed: {
        if (event.isAutoRepeat)
            return;

        if (api.keys.isCancel(event)) {
            event.accepted = true;
            return root.close();
        }
        if (api.keys.isNextPage(event) || api.keys.isPrevPage(event)) {
            event.accepted = true;
            return;
        }
    }

    Text {
        id: title
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: root.height * 0.18
        padding: parent.width * 0.025

        text: game.title
        elide: Text.ElideRight
        color: "#eee"
        font.pixelSize: height * 0.5
        font.family: global.fonts.condensed
        font.bold: true
        verticalAlignment: Text.AlignVCenter
    }

    Rectangle {
        id: leftbar
        anchors.top: title.bottom
        anchors.bottom: bottombar.top
        anchors.left: parent.left
        width: parent.width * 0.1
        color: "#222"

        ListView {
            id: leftbarList
            anchors.fill: parent
            anchors.topMargin: leftbar.height * 0.05
            anchors.bottomMargin: anchors.topMargin

            model: ["text", "media", "info"]
            readonly property string current: model[currentIndex]

            delegate: Rectangle {
                width: leftbar.width
                height: leftbar.height * 0.3
                color: ListView.isCurrentItem ? root.color : leftbar.color

                Image {
                    width: parent.width * 0.8
                    height: width
                    anchors.centerIn: parent

                    source: "assets/" + modelData + ".svg"
                    sourceSize { width: 64; height: 64 }
                    asynchronous: true
                }
            }
        }
    }

    PegasusUtils.AutoScroll {
        id: description
        anchors.left: leftbar.right
        anchors.top: title.bottom
        anchors.right: title.right
        anchors.bottom: bottombar.top
        visible: leftbarList.current == "text"

        Text {
            color: "#eee"
            text: game.description
            width: parent.width
            wrapMode: Text.WordWrap
            font.pixelSize: title.font.pixelSize * 0.6
            font.family: global.fonts.sans
            padding: title.padding
        }
    }

    Rectangle {
        anchors.left: leftbar.right
        anchors.right: parent.right
        anchors.top: title.bottom
        anchors.bottom: bottombar.top
        anchors.margins: title.padding

        color: "#111"
        visible: leftbarList.current == "media"
        onVisibleChanged: {
            if (visible) {
                videoDelay.restart();
            } else {
                videoDelay.stop();
                video.stop();
            }
        }

        Timer {
            id: videoDelay
            interval: 250
            onTriggered: {
                video.playlist.clear();
                game.assets.videos.forEach(v => video.playlist.addItem(v));
                video.play();
            }
        }
        Video {
            id: video
            visible: playlist.itemCount > 0

            anchors.fill: parent
            fillMode: VideoOutput.PreserveAspectFit

            playlist: Playlist {
                playbackMode: Playlist.Loop
            }
        }
        Text {
            text: "(this game has no video)"
            anchors.fill: parent
            anchors.margins: parent.width * 0.2
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: title.font.pixelSize * 0.6
            font.family: global.fonts.sans
            visible: !game.assets.videos.length
            color: "#eee"
        }
    }

    PegasusUtils.AutoScroll {
        id: details
        anchors.left: leftbar.right
        anchors.top: title.bottom
        anchors.right: title.right
        anchors.bottom: bottombar.top
        visible: leftbarList.current == "info"

        Column {
            anchors.left: parent.left
            anchors.right: parent.right

            Text {
                readonly property string playtime: {
                    const minutes = Math.ceil(game.playTime / 60)
                    return minutes <= 90
                        ? Math.round(minutes) + " minutes"
                        : parseFloat((minutes / 60).toFixed(1)) + " hours";
                }
                readonly property string lastplayed: {
                    if (isNaN(game.lastPlayed))
                        return "never";

                    var now = new Date();

                    var diffHours = (now.getTime() - game.lastPlayed.getTime()) / 1000 / 60 / 60;
                    if (diffHours < 24 && now.getDate() === game.lastPlayed.getDate())
                        return "today";

                    var diffDays = Math.round(diffHours / 24);
                    if (diffDays <= 1)
                        return "yesterday";

                    return diffDays + " days ago"
                }

                text: "<b>Play time:</b> " + playtime
                    + "<br><b>Last played:</b> " + lastplayed
                font.pixelSize: title.font.pixelSize * 0.6
                font.family: global.fonts.sans
                color: "#eee"
                padding: title.padding
                bottomPadding: 0
            }

            Text {
                text: "<b>Developer:</b> " + game.developer
                    + "<br><b>Publisher:</b> " + game.publisher
                font.pixelSize: title.font.pixelSize * 0.6
                font.family: global.fonts.sans
                color: "#eee"
                wrapMode: Text.WordWrap
                padding: title.padding
                bottomPadding: 0
            }

            Repeater {
                model: [game.genreList, game.tagList]
                delegate: Flow {
                    width: parent.width
                    padding: title.padding
                    spacing: title.font.pixelSize * 0.2

                    Repeater {
                        model: modelData
                        delegate: Text {
                            text: modelData
                            color: "#eee"
                            font.pixelSize: title.font.pixelSize * 0.6
                            font.family: global.fonts.sans
                            padding: font.pixelSize * 0.25
                            leftPadding: font.pixelSize * 0.5
                            rightPadding: leftPadding

                            Rectangle {
                                anchors.fill: parent
                                color: "#444"
                                z: -1
                            }
                        }
                    }
                }
            }
        }
    }

    ListView {
        id: bottombar

        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: parent.height * 0.125
        orientation: ListView.Horizontal

        readonly property var fns: [
            function() { root.close(); },
            function() { game.favorite = !game.favorite; },
            function() { game.launch(); },
        ]

        model: [
            { 'w': 1/5, 'icon': 'back' },
            { 'w': 1/5, 'icon': game.favorite ? 'heart_filled' : 'heart_empty' },
            { 'w': 3/5, 'icon': 'launch' },
        ]

        Keys.onPressed: {
            if (!event.isAutoRepeat && api.keys.isAccept(event)) {
                event.accepted = true;
                const idx = currentIndex;
                fns[idx]();
                bottombar.currentIndex = idx;
            }
        }

        delegate: Rectangle {
            width: ListView.view.width * modelData.w
            height: ListView.view.height
            color: ListView.isCurrentItem ? "#555" : "#444"

            Image {
                source: "assets/" + modelData.icon + ".svg"
                sourceSize { width: 64; height: 64 }
                asynchronous: true

                anchors.fill: parent
                anchors.margins: parent.height * 0.15
                fillMode: Image.PreserveAspectFit
            }
        }
    }
}
