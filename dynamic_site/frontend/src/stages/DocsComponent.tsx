import { DocsComponentsProps } from './Interfaces';

function DocsComponent(props: DocsComponentsProps) {
  return (
    <>
      <div
        id='{props.data.id}'
        className='uk-grid-small uk-child-width-1-1'
        data-uk-grid
      >
        <div className='uk-heading-bullet uk-margin-small-top uk-text-bolder uk-first-column'>
          {props.data.title}
        </div>
        <div dangerouslySetInnerHTML={{ __html: props.data.text }} />
      </div>
    </>
  );
}
export default DocsComponent;
