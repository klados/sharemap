$( document ).ready(function() {

	var prefix = '/sharemap';
	var onlineMembers = [];
	var markerList = [];
	var socket;

	if(modeMap == 'private'){
		socket = io.connect('http://' + document.domain + ':' + location.port);
		// socket = io.connect('http://' + document.domain + ':' + 5000);

		socket.on('connect', function() {
			socket.emit('initMap', {mapId: hash_path});
		});


		socket.on('markerChange', function(data){
			console.log('marker event', data);
			if(data.action == 'add'){
				console.log('recieve marker lat+lng ', data.lat+data.lng)

				let marker = addMarkerOnMap(data.lat, data.lng, data.markerName, (data.lat+data.lng) );
				markerList.push(marker);
				updateHtml();
			}
			else{
				for( i in markerList){
					if(markerList[i].id == data.markerId){
						markerList[i].setMap(null);	
						markerList.splice(i,1);
						break;
					}
				}

				let id = data.markerId.replace(/[.]/g,'');
				$('.'+id).remove();	
			}
		});

		socket.on('commentMarkerChange', function(data){

			$('.'+data.markerId).css('background-color','#4db6ac');
			$('#'+data.markerId).append(`
				<li class="collection-item" >`+data.username+':'+data.message+`
					<span class="secondary-content black-text">`+new Date().toUTCString()+`<span>
				</li>
			`)
		});

		socket.on('userMapChange', function(data){
			if(data.action == 'delete'){
				$('#'+data.username).remove();
				let i = onlineMembers.indexOf(data.username);
				if(i > -1) onlineMembers.splice(i,1);
			}
			else{
				$('#map_members').append(`
				<li class="collection-item" id="`+data[i].username+`" title='rank:user'>`+data.username+`
					<a href="#!" class="secondary-content removeFriendFromMap" title='Remove user'>
					<i class="material-icons blue-text" data-username='`+data.username+`'>delete</i></a>
				</li>
			`);
			}
		});

	}


	var map = new google.maps.Map(document.getElementById('map'), {
		center: {lat: 38.256, lng: 21.748},
		zoom: 12
	});


	// click to add marker
	google.maps.event.addListener(map, 'click', function(event) {
		let markerName = prompt('Give the name of the marker');
		if(markerName == null)return; // do nothing

		let lat = event.latLng.lat();
		let lng = event.latLng.lng();
		let id = lat.toString()+lng;
		let map_id = hash_path;

		fetch( prefix+'/addMarkerToMap',{
			method: 'POST', 
			body: JSON.stringify({'mapId': map_id, 'lat': lat,'lng': lng, 'title': markerName}), 
			headers:{
				'Content-Type': 'application/json'
			}
		})
			.then(function(response) {
				if(response.status != 200){
					M.toast({html: 'This is a public map', classes: 'rounded'});
					return;
				}
				return response.json();
			})
			.then(function(myJson) {
				if( parseInt(myJson) <0 ){
					M.toast({html: 'Error, please refresh the page', classes: 'rounded'});
				}
				else{
					let marker = addMarkerOnMap(event.latLng.lat(), event.latLng.lng(), markerName, id);
					markerList.push(marker);
					updateHtml();
					if( socket !== undefined ){
						socket.emit('markerChange', {'action':'add', 'lat':event.latLng.lat().toString(), 'lng':event.latLng.lng().toString(),'markerName':markerName, 'mapId': map_id});
					}
				}
			});

	});


	function addMarkerOnMap(lat, lng, markerName, id){

		let marker = new google.maps.Marker({
			position: {lat:parseFloat(lat), lng:parseFloat(lng)},
			title: markerName,
			id: id,
			map: map
		});

		let fix_id = id.toString();
		fix_id = fix_id.replace(/[.]/g,'');

		let contentHtml = `
						<div>
							<h5 class='center'>`+markerName+`</h5>
							<p>Conversation:</p>
							<ul class='chat collection' id='`+fix_id+`'></ul>

							<div class="row msgField">
									<div class="input-field col s8">
											<input id='postmsg' type="text" class=" validate">
											<label for="postmsg">Type your message</label>
									</div>
									<div class="input-field col s4">
										<button data-marker_id='`+id+`' class="postMsg btn waves-effect waves-light" type="text">Post</button>
									</div>
							</div>

						</div>	
					`;

		var infowindow = new google.maps.InfoWindow({
			content: contentHtml
		});

		marker.addListener('click', function() {
			$('.'+fix_id).css('background-color','#ffffff');
			infowindow.open(map, marker);
			getCommentsOfMarker(id);
		});

		return marker;
	}


	//updateHtml()
	function updateHtml(){
		$('#mapMarkers').empty();
		for(i in markerList){
			let noDots = markerList[i].id;
			noDots =  noDots.toString().replace(/[.]/g,'');

			$('#mapMarkers').append(`
				<li class='collection-item markerItem `+noDots+`' >`+markerList[i].title +
				`<a href="#!" class="secondary-content removeMarkerFromMap" data-id='`+markerList[i].id+`' title='Remove marker'>
					<i class="material-icons red-text" >delete</i>
				</a>
				<a href="#!" class="secondary-content focusOnMarker" data-id='`+markerList[i].id+`' title='Focus on Marker'>
					<i class="material-icons blue-text" >filter_center_focus</i>
				</a>
				</li>`
			);
		}
	}


	getMarkersFromDb();
	function getMarkersFromDb(){
		let map_id = hash_path;

		fetch(prefix+'/getMarkersFromMap/'+map_id)
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				if( parseInt(myJson) < 0){
					M.toast({html: 'Error, can not load the markers', classes: 'rounded'});
				}
				else{
					let data = myJson;
					for(i in data){
						let marker = addMarkerOnMap(data[i].lat, data[i].lng, data[i].title, data[i].lat+data[i].lng);
						markerList.push(marker);
						updateHtml();
					}
				}
			});
	}


	$(document).on('click','.postMsg', function(){
		let mapId = hash_path;
		let markerId= $(this).data('marker_id').toString(); 
		let message = $(this).parent().parent().find('.input-field input').val();
		gthis = this;

		console.log('post msg', markerId, message)

		fetch(prefix+'/postMessageOnMarker',{
			method: 'POST', 
			body: JSON.stringify({'mapId': mapId, 'markerId': markerId, 'message':message}), 
			headers:{
				'Content-Type': 'application/json'
			}
		})
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson){
				if( parseInt(myJson) <0){
					M.toast({html: 'Error, action failed', classes: 'rounded'});
				}
				else{
					$(gthis).parent().parent().find('.input-field input').val('');
					markerId = markerId.replace(/[.]/g,'');

					$('#'+markerId).append(`
							<li class="collection-item" >`+myUsername+':'+message+`
								<span class="secondary-content black-text">`+new Date().toUTCString()+`<span>
							</li>
						`);

					if( socket !== undefined )
					socket.emit('commentMarkerChange', {
						'username': myUsername, 
						'message': message,
						'markerId': markerId,
						'mapId': mapId
					});
				}
			});
	});


	function getCommentsOfMarker(markerId){
		let map_id = hash_path;

		fetch(prefix+'/getMessagesOfMarker/'+map_id+'/'+markerId)
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				if( parseInt(myJson) <0){
					if(parseInt(myJson) != -3)  // no messages available
						M.toast({html: 'Error, action failed', classes: 'rounded'});
				}
				else{
					let data = myJson;
					let fix_marker_id = markerId.replace(/[.]/g,'');

					$('#'+fix_marker_id).empty();

					for(i in data){
						// console.log('loop', data[i], fix_marker_id)
						$('#'+fix_marker_id).append(`
							<li class="collection-item" ><b>`+data[i].username+'</b>: '+data[i].msg+`
							<span class="secondary-content black-text">`+data[i].datetime+`<span>
						</li>
						`);
					}
				}
			});
	}


	//focus on marker
	$(document).on('click','.focusOnMarker',function(){
		let index;
		for( i in markerList){
			if( $(this).data('id') == markerList[i].id ){
				index = i;
				break;
			}
		}
		map.setCenter(markerList[index].getPosition());
	})


	$(document).on('click','.removeMarkerFromMap', function(){
		let mapId = hash_path;
		let markerId= $(this).data('id'); 
		let gthis = this;

		fetch(prefix+'/deleteMarkerFromMap',{
			method: 'POST', 
			body: JSON.stringify({'mapId': mapId, 'markerId': markerId}), 
			headers:{
				'Content-Type': 'application/json'
			}
		})
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson){
				if( parseInt(myJson) <0){
					M.toast({html: 'Error, action failed', classes: 'rounded'});
				}
				else{
					// remove marker from list
					$(gthis).parent().remove();
					// remove marker from map
					for( i in markerList){
						if( markerList[i].id == markerId){
							if(socket != undefined)
							socket.emit('markerChange', {'action':'delete','markerId': markerList[i].id, 'mapId': mapId});
							markerList[i].setMap(null);	
							markerList.splice(i,1);
							break;
						}
					}

				}
			});
	});


	getMembersOfMap();
	function getMembersOfMap(){
		let map_id = hash_path;

		fetch(prefix+'/getMembersOfMap/'+map_id)
			.then(function(response) {
				//console.log(response.status)
				if(response.status != 200){
					M.toast({html: 'This is a public map', classes: 'rounded'});
					return -1;
				}
				return response.json();
			})
			.then(function(myJson) {
				if(parseInt(myJson) < 0){
					$('#map_members').append('Problem, please refresh the page');
				}
				else{
					let data = myJson;
					for(i in data){
						onlineMembers.push(data[i].username);
						$('#map_members').append(`
						<li class="collection-item" title='rank:`+data[i].role+`'>`+data[i].username+`
						<a href="#!" class="secondary-content removeFriendFromMap" title='Remove user'>
						<i class="material-icons blue-text" data-username='`+data[i].username+`'>delete</i></a>
						</li>
						`);
					}
				}
			});
	}


	$(document).on('click','.removeFriendFromMap',function(){
		let mapId = hash_path;
		let username = $(this).find('i').data('username'); 
		let gthis = this;

		fetch(prefix+'/removeFriendFromMap',{
			method: 'POST', 
			body: JSON.stringify({'mapId': mapId, 'username': username}), 
			headers:{
				'Content-Type': 'application/json'
			}
		})
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson){
				console.log('myjs', myJson)
				if( parseInt(myJson) <0){
					if(parseInt(myJson) == -2){
						M.toast({html: 'You do not own the map, action failed', classes: 'rounded'});
					}
					else M.toast({html: 'Error, action failed', classes: 'rounded'});
				}
				else{
					//remove username from list
					$(gthis).parent().remove();
					let i = onlineMembers.indexOf(username);
					if(i > -1) onlineMembers.splice(i,1);
					// console.log('onlineMembers', onlineMembers)
					if(socket != undefined)
					socket.emit('userMapChange', {'action':'delete', 'username': username, 'mapId': mapId});
				}
			});
	});


	$('#searchFriend').keyup(function(){

		fetch(prefix+'/findFriend?txt='+ $('#searchFriend').val())
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson){
				//console.log('myjson', myJson)
				$('#inviteFriendsList').empty();
				if(myJson == '-1'){
					$('#inviteFriendsList').append('Problem, please refresh the page');
				}
				else{
					let data = myJson;
					for(i in data){
						if( onlineMembers.includes(data[i].username) ) continue;
						$('#inviteFriendsList').append(`
						<li class="collection-item" >`+data[i].username+`
						<a href="#!" class="secondary-content inviteFriend blue-text" title='Invite user'>
						<i class="material-icons" data-username='`+data[i].username+`'>person_add</i></a>
						</li>
							`);
					}
				}
			});
	});


	$(document).on('click', '.inviteFriend', function(){
		// console.log('invite friend', $(this).find('i').data('username') );

		let mapId = hash_path;
		let username = $(this).find('i').data('username'); 

		fetch(prefix+'/inviteFriendToMap',{
			method: 'POST', 
			body: JSON.stringify({'mapId': mapId, 'username': username}), 
			headers:{
				'Content-Type': 'application/json'
			}
		})
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson){
				console.log('myjson', myJson)
				if(parseInt(myJson) < 0){
					$('#inviteFriendsList').append('Problem, please refresh the page');
				}
				else{
					// $(this).parent().remove(); // remove user from search list
					$('#inviteFriendsList').empty(); // clear results
					$('#searchFriend').val(''); //clear search input
					//add user to the member's list
					$('#map_members').append(`
						<li class="collection-item" id="`+username+`" title='rank:user'>`+username+`
						<a href="#!" class="secondary-content removeFriendFromMap" title='Remove user'>
						<i class="material-icons blue-text" data-username='`+username+`'>delete</i></a>
						</li>
						`);
					M.toast({html: 'User invited !!!', classes: 'rounded'});
					if(socket != undefined)
					socket.emit('userMapChange', {'action':'invite', 'username': username, 'mapId': mapId});
				}
			});
	});


	// $('.fixed-action-btn').floatingActionButton();
	// var elems = document.querySelectorAll('.fixed-action-btn');
	// var instances = M.FloatingActionButton.init(elems, {
	// 	direction: 'left',
	// 	hoverEnabled: false
	// });

});


