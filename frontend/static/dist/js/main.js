function toggleDisplay(id)
{
	element = document.getElementById(id);
	(element.style.display == 'block') ? element.style.display = 'none' : element.style.display = 'block';
}