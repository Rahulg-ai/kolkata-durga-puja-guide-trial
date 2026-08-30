import "./PandalCard.css";


type PandalCardProps = {
  name: string;
  area: string;
  metroStation: string;
  selected: boolean;
  onClick: () => void;
};


function PandalCard({
  name,
  area,
  metroStation,
  selected,
  onClick,
}: PandalCardProps) {

  return (
    <button
      type="button"
      className={`compact-pandal-card ${
        selected
          ? "selected"
          : ""
      }`}
      onClick={onClick}
    >

      <div className="compact-pandal-icon">
        🎉
      </div>


      <div className="compact-pandal-info">

        <h2>
          {name}
        </h2>


        <p>
          📍 {area}
        </p>


        <p>
          🚇 {metroStation}
        </p>

      </div>


      <div className="compact-pandal-check">

        {selected
          ? "✓"
          : ""}

      </div>

    </button>
  );
}


export default PandalCard;