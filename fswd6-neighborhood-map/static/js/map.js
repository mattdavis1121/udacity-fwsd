function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 40.04443758460856, lng: -94.8779296875},
        zoom: 4
    });

    mapBounds = new google.maps.LatLngBounds();
    geo = new google.maps.Geocoder();
}

function makeMarker(breweryModel) {
    var marker = new google.maps.Marker({
        // map: map,
        position: breweryModel.coords(),
        title: breweryModel.name(),
        animation: google.maps.Animation.DROP,
        icon: '../static/img/dark-green-marker-med.png'
    });
    marker.addListener('click', function () {
        console.log(this.breweryObj.viewModel.locationClick(this.breweryObj));
    });
    mapBounds.extend(marker.position);
    map.fitBounds(mapBounds);
    return marker;
}
